import sys
sys.path.append(r'C:\Users\frede\PycharmProjects\aCar_MCVRPTW\heuristics')
from heuristics.MCVRPTW import MCVRPTW
import random as rnd

for i in range(1):
    n = 100
    p = 5
    radius = 20
    Coordinates = {i: (rnd.randint(-radius, radius), rnd.randint(-radius, radius)) for i in range(n + 1)}
    Customer_demands = {i: [int(rnd.random() + 0.7) * rnd.randint(0, 10) for product in range(p)] for i in
                        range(1, n + 1)}
    Vehicle_parameters = {'lenght_capacity': 200, 'speed': 1,
                          'product_capacity': {product: 200 for product in range(p)}}
    Earliest_service_time = [0] + [rnd.randint(0, 850) for i in range(n)] + [0]
    Latest_service_time = [1000] + [Earliest_service_time[i + 1] + rnd.randint(50, 150) for i in range(n)]
    Service_time = {i: 10 for i in range(1, n + 1)}
    Service_time[0] = 0
    VRP = MCVRPTW(Coordinates=Coordinates, Customer_demands=Customer_demands, Vehicle_parameters=Vehicle_parameters,
                   Earliest_service_time=Earliest_service_time, Latest_service_time=Latest_service_time,
                   Service_time=Service_time)
    VRP.all_run()
    VRP.display_solution()
    print('Routes:',VRP.Routes)
    # print('Arrival_time_with_...:',VRP.Arrival_time_with_same_order_than_Routes)