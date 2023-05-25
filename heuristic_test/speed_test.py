import sys
sys.path.append(r'C:\Users\frede\PycharmProjects\aCar_MCVRPTW\heuristics')
from heuristics.MCVRPTW import MCVRPTW
import time
import pandas as pd
from heuristics.Bayesian_optimisation import bayesian_optimisation

Number_of_customers = [2**i for i in range(4,9)]
Time_1_products = []
Time_3_products = []
Time_6_products = []
Time_10_products = []

df = pd.read_csv('50_customers_data.csv')
index = 0
for p in [1,10]:
    print(p)
    for m in range(4,9):
        print(m)
        Data = []
        for i in range(15):
            n = 2 ** m
            Coordinates = {j:eval(df.Coordinates_set.iloc[i])[j] for j in range(n)}
            Customer_demands = {j:eval(df.eval('Customer_demands_p' + str(p) + '_set').iloc[i])[j] for j in range(n)}
            Vehicle_parameters = {'lenght_capacity': 200, 'speed': 1,
                                  'product_capacity': {product: 100 for product in range(p)}}
            Earliest_service_time = eval(df.Earliest_service_time_set.iloc[i])[:n]+[0]
            Latest_service_time = eval(df.Latest_service_time_set.iloc[i])[:n]
            Service_time = {i: 10 for i in range(1, n + 1)}
            Service_time[0] = 0
            start = time.time()
            Data_results = bayesian_optimisation(Coordinates=Coordinates, Customer_demands=Customer_demands,
                                                 Vehicle_parameters=Vehicle_parameters,
                                                 Earliest_service_time=Earliest_service_time,
                                                 Latest_service_time=Latest_service_time,
                                                 Service_time=Service_time)
            MCVRPTW_ = MCVRPTW(Coordinates=Coordinates, Customer_demands=Customer_demands,
                               Vehicle_parameters=Vehicle_parameters,
                               Earliest_service_time=Earliest_service_time, Latest_service_time=Latest_service_time,
                               Service_time=Service_time, hyperparameter_impact1=Data_results['hyperparameter_impact1'],
                               hyperparameter_impact2=Data_results['hyperparameter_impact2'],
                               hyperparameter_impact3=Data_results['hyperparameter_impact3'],
                               hyperparameter_impact4=Data_results['hyperparameter_impact4'])
            MCVRPTW_.heuristic()
            MCVRPTW_.check_all_is_allright()
            end = time.time()
            Data.append(end-start)
        print(Data)
        eval('Time_' + str(p)+'_products').append(Data)
        index +=1



Data_for_csv = {
    'Number_of_customers' : Number_of_customers,
    'Time_1_products' : Time_1_products,
    # 'Time_3_products' : Time_3_products,
    # 'Time_6_products' : Time_6_products,
    'Time_10_products' : Time_10_products
}

df = pd.DataFrame(Data_for_csv)
df.to_csv('speed_test_withBO.csv',index=False)