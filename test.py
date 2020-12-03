import unittest
from homework7852.process_covid import (load_covid_data,
                                        cases_per_population_by_age,
                                        hospital_vs_confirmed,
                                        create_confirmed_plot,
                                        count_high_rain_low_tests_days,
                                        compute_running_average)
# global file path
file = r"C:/Users/Administrator/Desktop/7820/ER-Mi-EV_2020-03-16_2020-04-24.json"
class CovidTest(unittest.TestCase):
    def testLoadData(self):
        """ test function load_covid_data() return dict or not """
        data = load_covid_data(file)
        assert type(data).__name__ == 'dict'

    def testhospital_vs_confirmed(self):
        """ the expected output even when some values are missing"""
        data = load_covid_data(file)
        aim_day = data['evolution']['2020-03-16']
        # Artificial cut one value , it supposed to be 4 number
        aim_day['epidemiology']['confirmed']['total']['age'] = [10, 11, 12]
        try:
            cases_population = cases_per_population_by_age(data)
        except Exception as e:
            raise Exception

    def testgenerate_data_plot_confirm(self):
        data = load_covid_data(file)
        create_confirmed_plot(data, sex=4)

    def testcompute_running_average(self):
        data = [0, 1, 5, 2, 2, 5]
        res = compute_running_average(data, 3)
        assert res == [None, 2.0, 2.667, 3.0, 3.0, None]

        res = compute_running_average(data, 4)
        assert res == [None, None, None, 2.0, 2.5, 3.5]

