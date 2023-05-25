import sys
sys.path.append(r'C:\Users\frede\PycharmProjects\aCar_MCVRPTW\heuristics')
from heuristics.MCVRPTW import MCVRPTW
import pandas as pd

name='C204.100'

[name_of_problem,number_of_customer] = name.split('.')
number_of_customer = int(number_of_customer)

with open('../Dataset/benchmarking_dataset/dataset'+name_of_problem+'.csv') as csvfile:
    Data = pd.read_csv(csvfile)

Coordinates = {i: eval(Data['Coordinates'][i]) for i in range(number_of_customer+1)}
Customer_demands = {i: eval(Data['Customer_demands'][i]) for i in range(number_of_customer+1)}
Vehicle_parameters = {'lenght_capacity': 20000, 'speed': 100,
                      'product_capacity': Data['Vehicle_capacity']}
Earliest_service_time = [eval(Data['Earliest_service_time'][i])[0] for i in range(number_of_customer+1)]
Earliest_service_time.append(0)
Latest_service_time = [eval(Data['Latest_service_time'][i])[0] for i in range(number_of_customer+1)]
Latest_service_time.append(2000)
Service_time = {i: Data['Service_time'][i] for i in range(number_of_customer+1)}
MCVRPTW_ = MCVRPTW(Coordinates=Coordinates, Customer_demands=Customer_demands, Vehicle_parameters=Vehicle_parameters,
               Earliest_service_time=Earliest_service_time, Latest_service_time=Latest_service_time,
               Service_time=Service_time)
MCVRPTW_.all_run()
# MCVRPTW_.heuristic()
# MCVRPTW_.check_all_is_allright()
# MCVRPTW_.compute_done_distance()
# MCVRPTW_.display_customers()
# MCVRPTW_.display_solution()
# print(MCVRPTW_.Problems)
# print(len(MCVRPTW_.Routes))
# print(MCVRPTW_.Routes)
# print(MCVRPTW_.Arrival_time_with_same_order_than_Routes)
# print(MCVRPTW_.Distance_done[0])
# print(bayesian_optimisation(Coordinates=Coordinates, Customer_demands=Customer_demands, Vehicle_parameters=Vehicle_parameters,
#                Earliest_service_time=Earliest_service_time, Latest_service_time=Latest_service_time,
#                Service_time=Service_time))