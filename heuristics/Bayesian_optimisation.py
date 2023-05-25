
from skopt import gp_minimize
from skopt.space import Real, Integer
from skopt.utils import use_named_args
from MCVRPTW import MCVRPTW
import time

"""
in this file, the bayesian optimisation has been adapted to our heuristic in order to tune it and to improve the results.
it is very easy to use : you just need to call the function bayesian_optimisation and to give the input, exactly as for the heuristic
"""

def bayesian_optimisation(Coordinates, Customer_demands,Vehicle_parameters,Earliest_service_time, Latest_service_time, Service_time):
    start = time.time()
    space = [
        Real(0.02, 0.3, name='hyperparameter_impact1'),
        Real(0.2, 0.5, name='hyperparameter_impact2'),
        Real(0.02, 0.3, name='hyperparameter_impact3'),
        Real(0.3, 0.7, name='hyperparameter_impact4')
    ]
    Hyperparameters = {
        'n_calls': 100,
        'n_initial_points': 10,
        'noise': 0,
        'xi': 0.01,
        'problem_set': ''
    }
    @use_named_args(space)
    def objective_function(**params):
        # Create an instance of the ALNS algorithm with the given hyperparameters
        MCVRPTW_ = MCVRPTW(Coordinates=Coordinates, Customer_demands=Customer_demands,
                           Vehicle_parameters=Vehicle_parameters,
                           Earliest_service_time=Earliest_service_time, Latest_service_time=Latest_service_time,
                           Service_time=Service_time,
                           hyperparameter_impact1=params['hyperparameter_impact1'],
                           hyperparameter_impact2=params['hyperparameter_impact2'],
                           hyperparameter_impact3=params['hyperparameter_impact3'],
                           hyperparameter_impact4=params['hyperparameter_impact4'])
        MCVRPTW_.heuristic()
        MCVRPTW_.compute_done_distance()
        return MCVRPTW_.Distance_done[0]

    result = gp_minimize(objective_function, space, n_calls=Hyperparameters['n_calls'], n_initial_points=Hyperparameters['n_initial_points'], noise=Hyperparameters['noise'], xi=Hyperparameters['xi'], n_jobs=-1, acq_func='EI')
    Data_results = {**{**{'TD': result.fun}, **{'NV':0}}, **dict(
        zip(['hyperparameter_impact1', 'hyperparameter_impact2', 'hyperparameter_impact3', 'hyperparameter_impact4'],
            result.x))}
    MCVRPTW_bo = MCVRPTW(Coordinates=Coordinates, Customer_demands=Customer_demands,
                       Vehicle_parameters=Vehicle_parameters,
                       Earliest_service_time=Earliest_service_time, Latest_service_time=Latest_service_time,
                       Service_time=Service_time,
                       hyperparameter_impact1=Data_results['hyperparameter_impact1'],
                       hyperparameter_impact2=Data_results['hyperparameter_impact2'],
                       hyperparameter_impact3=Data_results['hyperparameter_impact3'],
                       hyperparameter_impact4=Data_results['hyperparameter_impact4'])
    MCVRPTW_bo.heuristic()
    Data_results['NV']=len(MCVRPTW_bo.Routes)
    end =time.time()
    Data_results = {**Data_results,**{'time':end-start,'delivery time':MCVRPTW_bo.Arrival_time,'needed capacity':MCVRPTW_bo.Capacity_related_to_Routes}}
    return Data_results




