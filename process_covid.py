# FIXME add needed imports
import matplotlib.pyplot as plt
from typing import Dict, List, Tuple
import json
"""
json structure
metadata: 
    time-range
    age_binning: hospitalizations,population
region:
    name
    ...
    population: total, male, female, age
    ...
evolution
    time:
        hospitalizations
            hospitalized
                new
                total
                current
            intensive_care
                ...
            ventilator
                ...
        epidemiology
        ...
"""


def load_covid_data(filepath):
    with open(filepath, 'r') as f:
        data = json.load(f)
    return data


def cases_per_population_by_age(input_data: dict) -> Dict[
    str, List[Tuple[str, float]]]:
    population_range = input_data['metadata']['age_binning']['population']
    hospital_range = input_data['metadata']['age_binning']['hospitalizations']
    pop_number = input_data['region']['population']['age']
    pop_dic = dict(zip(population_range, pop_number))
    day_age = {}
    for day, sub_dic in input_data['evolution'].items():
        confirmed = sub_dic['epidemiology']['confirmed']['total']['age']
        percent = [confirmed[i]/pop_number[i] for i in range(len(population_range))]
        day_age[day] = dict(zip(population_range, percent))
    age_day = {}
    for day, age in day_age.items():
        for age_, per in age.items():
            if age_ not in age_day:
                age_day[age_] = [(day, per)]
            else:
                age_day[age_].append((day, per))

    return age_day


def hospital_vs_confirmed(input_data):
    day_list = []
    ratio = []
    for day, sub_dic in input_data['evolution'].items():
        day_list.append(day)
        new_hos = sub_dic['hospitalizations']['hospitalized']['new']['all']
        new_conf = sub_dic['epidemiology']['confirmed']['new']['all']
        ratio.append(round(new_hos / new_conf, 2))
    return (day_list, ratio)


def generate_data_plot_confirmed(input_data, sex=False, max_age=-1, status='total'):
    """
    At most one of sex or max_age allowed at a time.
    sex: only 'male' or 'female'
    max_age: sums all bins below this value, including the one it is in.
    status: 'new' or 'total' (default: 'total')
    """
    if sex:
        out_data = {'date':[], 'value':[]}
        for day, sub_dic in input_data['evolution'].items():
            conf = sub_dic['epidemiology']['confirmed'][status]
            out_data['date'].append(day)
            out_data['value'].append(conf[sex])
        return out_data

    hospital_range = input_data['metadata']['age_binning'][
        'hospitalizations']
    max_age_ls = []
    age_flag = ''
    # if max_age_ls <= 0:
    #     max_age_ls = list(range(len(hospital_range)))
    # else:
    for index in range(len(hospital_range)):
        age_range = hospital_range[index].split('-')
        if age_range[1].strip() != '':
            if int(age_range[0].strip()) <= max_age <= int(age_range[1].strip()):
                age_flag = age_range[1].strip()
                max_age_ls = list(range(index+1, len(hospital_range)))
                break
        else:
            age_flag = age_range[0].strip()
            max_age_ls = [-1]
    out_data = {'date':[], 'value':[]}
    for day, sub_dic in input_data['evolution'].items():
        conf_age = sub_dic['epidemiology']['confirmed'][status]['age']
        out_data['date'].append(day)
        count = 0
        for ind in max_age_ls:
            count += conf_age[ind]
        out_data['value'].append(count)
    return out_data, age_flag



def create_confirmed_plot(input_data, sex=False, max_ages=[], status='total',
                          save=False):
    # FIXME check that only sex or age is specified.
    if not sex and len(max_ages) == 0:
        raise ValueError('Please enter correct params!!')
    if sex and len(max_ages) != 0:
        raise ValueError('At most one of sex or max_age allowed at a time!!')
    fig = plt.figure(figsize=(10, 10))
    # FIXME change logic so this runs only when the sex plot is required
    if sex:
        for sex in ['male', 'female']:
            # FIXME need to change `changeme` so it uses generate_data_plot_confirmed
            data = generate_data_plot_confirmed(input_data,sex=sex,max_age=-1,status=status)
            if sex == 'male':
                plt.plot('date', 'value', data=data, label=f'{status} {sex}', color='green')
            else:
                plt.plot('date', 'value', data=data, label=f'{status} {sex}',
                         color='purple')
    # FIXME change logic so this runs only when the age plot is required
    else:
        for age in max_ages:
            # FIXME need to change `changeme` so it uses generate_data_plot_confirmed
            color = ''
            if age <= 25:
                color = 'green'
            elif age <= 50:
                color = 'orange'
            elif age <= 75:
                color = 'purple'
            else:
                color = 'pink'
            data,age_flag = generate_data_plot_confirmed(input_data, sex=False, max_age=age,
                                                status=status)
            plt.plot('date', 'value', data=data, label=f'{status} younger than {age_flag}',c=color)
    fig.autofmt_xdate()  # To show dates nicely
    # TODO add title with "Confirmed cases in ..."
    title = f"Confirmed cases in {input_data['region']['name']}"
    plt.title(title)
    # TODO Add x label to inform they are dates
    plt.xlabel('Data')
    # TODO Add y label to inform they are number of cases
    plt.ylabel('Cases')
    # TODO Add legend
    plt.legend()
    # TODO Change logic to show or save it into a '{region_name}_evolution_cases_{type}.png'
    #      where type may be sex or age
    type_ = 'sex' if sex else 'age'
    region_name = input_data['region']['name']
    if save:
        plt.savefig(f'{region_name}_evolution_cases_{type_}.png')
    else:
        plt.show()


def compute_running_average(data, window):
    side = (window-1)//2
    result = data.copy()
    n = len(data)
    for i in range(side, n-side):
        temp = data[i-side:i+side+1]
        count = 0
        for j in temp:
            if j is None:
                window -= 1
            else:
                count += j

        result[i] = round(count/window,3)
    result[:side] = [None]*side
    result[-side:] = [None] * side
    return result


def simple_derivative(data):
    if len(data) == 0:
        return []
    else:
        result = [None]
        for i in range(1, len(data)):
            if data[i] is None or data[i-1] is None:
                result.append(None)
            else:
                result.append(data[i]-data[i-1])
        return result



def count_high_rain_low_tests_days(input_data):
    test = []
    rain = []
    for day, sub_dic in input_data['evolution'].items():
        rain_ = sub_dic['weather']['rainfall']
        test_ = sub_dic['epidemiology']['tested']['new']['all']
        test.append(test_)
        rain.append(rain_)
    # smooth
    smooth_test = compute_running_average(test, 7)
    smooth_rain = compute_running_average(rain, 7)
    # derivative
    der_test = simple_derivative(smooth_test)
    der_rain = simple_derivative(smooth_rain)
    # calculate
    days_rain_up = [index for index in range(len(der_rain)) if der_rain[index] is not None and der_rain[index] > 0]
    days_rain_up_test_down = [index for index in days_rain_up if
                              der_test[index] is not None and
                              der_test[index] < 0]
    return len(days_rain_up_test_down)/len(days_rain_up)