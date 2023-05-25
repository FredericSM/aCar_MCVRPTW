import sys
sys.path.append(r'C:\Users\frede\PycharmProjects\aCar_MCVRPTW\heuristics')
from heuristics.MCVRPTW import MCVRPTW
import pandas as pd
import numpy as np
from heuristics.Bayesian_optimisation import bayesian_optimisation

Name = {
    # 'solutionC100_200.csv',
    # 'solutionR100_200.csv'
    'solutionRC100_200.csv'
}

Name_of_Problem = []
Number_of_customer = []
LowerBound = []
NV = []
SNV = []
ATD = []
ETD = [] # exact solution
HP1 = []
HP2 = []
HP3 = []
HP4 = []
Time = []

for name in Name:
    with open('../Dataset/results_heuristic_test/'+name) as csvfile:
        Solution = pd.read_csv(csvfile)
    Solution = Solution.dropna()
    Solution = Solution.reset_index(drop=True)
    Problem = Solution['Problem']
    Distance = Solution['Distance']
    Number_of_vehicle = Solution['NV']
    for i in range(len(Problem)):
        if Problem[i]!= np.nan and Distance[i]!= np.nan and Number_of_vehicle[i]!=np.nan:
            [name_of_problem,number_of_customer] = Problem[i].split('.')
            print(Problem[i])
            number_of_customer = int(number_of_customer)
            opt_distance = Distance[i]
            with open('../Dataset/benchmarking_dataset/dataset'+name_of_problem+'.csv') as csvfile:
                Data = pd.read_csv(csvfile)
            Coordinates = {i: eval(Data['Coordinates'][i]) for i in range(number_of_customer+1)}
            Customer_demands = {i: eval(Data['Customer_demands'][i]) for i in range(number_of_customer+1)}
            Vehicle_parameters = {'lenght_capacity': 10000, 'speed': 100,
                                  'product_capacity': [Data['Vehicle_capacity'][0]]}
            Earliest_service_time = [eval(Data['Earliest_service_time'][i])[0] for i in range(number_of_customer+2)]
            Latest_service_time = [eval(Data['Latest_service_time'][i])[0] for i in range(number_of_customer+2)]
            Service_time = {i: Data['Service_time'][i] for i in range(number_of_customer+1)}
            Data_results = bayesian_optimisation(Coordinates=Coordinates, Customer_demands=Customer_demands, Vehicle_parameters=Vehicle_parameters,
               Earliest_service_time=Earliest_service_time, Latest_service_time=Latest_service_time,
               Service_time=Service_time)
            MCVRPTW_ = MCVRPTW(Coordinates=Coordinates, Customer_demands=Customer_demands, Vehicle_parameters=Vehicle_parameters,
                           Earliest_service_time=Earliest_service_time, Latest_service_time=Latest_service_time,
                           Service_time=Service_time,hyperparameter_impact1=Data_results['hyperparameter_impact1'],
                               hyperparameter_impact2=Data_results['hyperparameter_impact2'],
                               hyperparameter_impact3=Data_results['hyperparameter_impact3'],
                               hyperparameter_impact4=Data_results['hyperparameter_impact4'])
            MCVRPTW_.heuristic()
            MCVRPTW_.compute_done_distance()
            Name_of_Problem.append(name_of_problem)
            Number_of_customer.append(number_of_customer)
            LowerBound.append(int(sum([eval(Data['Customer_demands'][i])[0] for i in range(number_of_customer+1)])/Data['Vehicle_capacity'][0])+1)
            NV.append(len(MCVRPTW_.Routes))
            SNV.append(Number_of_vehicle[i])
            ATD.append(MCVRPTW_.Distance_done[0])
            ETD.append(opt_distance)
            Time.append(Data_results['time'])
            HP1.append(Data_results['hyperparameter_impact1'])
            HP2.append(Data_results['hyperparameter_impact2'])
            HP3.append(Data_results['hyperparameter_impact3'])
            HP4.append(Data_results['hyperparameter_impact4'])

Data_for_csv = {
    'Name of the set':Name_of_Problem,
    'Number of customer':Number_of_customer,
    'Lower Bound':LowerBound,
    'NV':NV,
    'SNV':SNV,
    'ATD':ATD,
    'ETD':ETD,
    'Time':Time,
    'HP1':HP1,
    'HP2':HP2,
    'HP3':HP3,
    'HP4':HP4
}
df = pd.DataFrame(Data_for_csv)
df.to_csv('Evaluation_with_tuning_RC.csv', index=False)
