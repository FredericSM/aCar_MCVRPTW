import sys
sys.path.append(r'C:\Users\frede\PycharmProjects\aCar_MCVRPTW\heuristics')
from heuristics.MCVRPTW_for_studycase import MCVRPTW
import pandas as pd
import math
import numpy as np

def convert_GPS_to_cart(latitude,longitude):
    R = 6371
    x = R * math.cos(math.pi/180*latitude) * math.cos(math.pi/180*longitude)
    y = R * math.cos(math.pi/180*latitude) * math.sin(math.pi/180*longitude)
    z = R * math.cos(math.pi/180*latitude)
    return (x,y,z)

def haversine_distance(lat1, lon1, lat2, lon2):
    # Convert latitude and longitude from degrees to radians
    lat1_rad = math.radians(lat1)
    lon1_rad = math.radians(lon1)
    lat2_rad = math.radians(lat2)
    lon2_rad = math.radians(lon2)

    # Haversine formula
    dlon = lon2_rad - lon1_rad
    dlat = lat2_rad - lat1_rad
    a = math.sin(dlat / 2) ** 2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    radius = 6371  # Earth's radius in kilometers
    distance = radius * c

    return distance


Set = [[7],[7,20,36,52],[7,20,24,28,35,36,52],[7,20,24,28,35,36,45,52,55,57],[7,10,13,20,24,28,35,36,45,48,52,55,57],[7,10,13,14,20,24,28,35,36,37,42,45,48,52,55,57],[2,7,10,13,14,20,24,28,29,35,36,37,42,43,45,48,52,55,57]]
# subset of Theresa
with open('../Dataset/Ethiopya_data/ET_locations.csv') as csvfile:
    Data_location = pd.read_csv(csvfile)
with open('../Dataset/Ethiopya_data/ET_demands.csv') as csvfile:
    Data_demands = pd.read_csv(csvfile)
with open('../Dataset/Ethiopya_data/ET_distance&time.csv') as csvfile:
    Data_distance_time = pd.read_csv(csvfile)

number_of_cluster = len(Data_location)
Latitude = [7.538002472] + [Data_location.iloc[i,1] for i in range(number_of_cluster-1)]  # Replace with your latitude values
Longitude = [39.2580316] + [Data_location.iloc[i,2] for i in range(number_of_cluster-1)]  # Replace with your longitude values
Index_to_id = {Data_location.iloc[i,0]:i+1 for i in range(number_of_cluster)}
Index_to_id[100] = 0
Id_to_index = {v: k for k, v in Index_to_id.items()}
Distance = []
Traveling_time = []
for i in range(number_of_cluster):
    distance = []
    traveling_time = []
    for j in range(number_of_cluster):
        distance.append(Data_distance_time.iloc[number_of_cluster*i+j,3])
        traveling_time.append(Data_distance_time.iloc[number_of_cluster*i+j,2])
    Distance.append(distance)
    Traveling_time.append(traveling_time)
Distance = [Distance[-1]]+Distance[:-1]
Distance = [[Distance[i][-1]]+Distance[i][:-1] for i in range(len(Distance))]
Traveling_time = [Traveling_time[-1]]+Traveling_time[:-1]
Traveling_time = [[Traveling_time[i][-1]]+Traveling_time[i][:-1] for i in range(len(Traveling_time))]
Distance = (np.array(Distance) + np.array(Distance).T)/2
n = 22

Cost = {'cost_per_km':0.0412, 'cost_per_vehicle':18000} #euros
#unit km, hour, euro,

# for set in Set:
#     Coordinates = {i: (Latitude[i], Longitude[i]) for i in range(number_of_cluster)}
#     Customer_demands = {
#         i + 1: [Data_demands.iloc[i, 1], Data_demands.iloc[i, 2], Data_demands.iloc[i, 3], Data_demands.iloc[i, 4] / 52]
#         for i in
#         range(number_of_cluster - 1)}
#     Customer_demands[0] = [0, 0, 0, 0]
#
#     Earliest_service_time = [8 for i in range(number_of_cluster + 2)]
#     Latest_service_time = [16 for i in range(number_of_cluster + 2)]
#
#     for i in range(len(Customer_demands)):
#         if Id_to_index[i] not in set:
#             Customer_demands[i] = [0,0,0,0]
#     n = int(max([Customer_demands[i][1] for i in range(len(Customer_demands))])/1105)+1
#     print('n',n)
#     Duration = {'WDS': 0.004167 / n, 'PNC': 0.25 / n, 'ED': 0.016 / n, 'ELEC': 0.000083 / n}  # hour
#     Service_time = {i + 1: max([Duration['WDS'] * Customer_demands[i + 1][0] + Duration['ELEC'] *
#                                 Customer_demands[i + 1][1] + Duration['ED'] * Customer_demands[i + 1][2] + Duration[
#                                     'PNC'] * Customer_demands[i + 1][3]]) for i in range(number_of_cluster - 1)}
#     Service_time[0] = 0
#     Vehicle_parameters = {'lenght_capacity': 200, 'speed': 1,
#                           'product_capacity': [n * 609, n * 1105, n * 345, n * 32]}  # WDS,ELEC,ED,PNC 50 kg+100kg
#
#     VRP = MCVRPTW(Coordinates=Coordinates,Distance=Distance,Travel_time=Traveling_time, Customer_demands=Customer_demands, Vehicle_parameters=Vehicle_parameters,
#                    Earliest_service_time=Earliest_service_time, Latest_service_time=Latest_service_time,
#                    Service_time=Service_time,Index_to_id=Index_to_id)
#     VRP.all_run()
#     # print(VRP.Distance_between_customers)
#     # VRP.display_customers()
#     VRP.display_solution()
#     # VRP.check_all_is_allright()
#
#     print('F.C:',(int(VRP.number_of_vehicle/5)+1)*Cost['cost_per_vehicle'])
#     print('TD:',VRP.traveled_distance*n)
#     print('NV:',VRP.number_of_vehicle*n)
#     Routes_ordered = []
#     for r in range(len(VRP.Routes)):
#         Routes_ordered.append([Id_to_index[VRP.Routes[r][i]] for i in range(len(VRP.Routes[r]))])
#     print('route:',Routes_ordered)

Coordinates = {i: (Latitude[i], Longitude[i]) for i in range(number_of_cluster)}
Customer_demands = {
        i + 1: [Data_demands.iloc[i, 1], Data_demands.iloc[i, 2], Data_demands.iloc[i, 3], Data_demands.iloc[i, 4] / 52]
        for i in
        range(number_of_cluster - 1)}
Customer_demands[0] = [0, 0, 0, 0]

Earliest_service_time = [8 for i in range(number_of_cluster + 2)]
Latest_service_time = [16 for i in range(number_of_cluster + 2)]
Duration = {'WDS': 0.004167 / n, 'PNC': 0.25 / n, 'ED': 0.016 / n, 'ELEC': 0.000083 / n}  # hour
Service_time = {i + 1: max([Duration['WDS'] * Customer_demands[i + 1][0] + Duration['ELEC'] *
                            Customer_demands[i + 1][1] + Duration['ED'] * Customer_demands[i + 1][2] + Duration[
                                'PNC'] * Customer_demands[i + 1][3]]) for i in range(number_of_cluster - 1)}
Service_time[0] = 0
Vehicle_parameters = {'lenght_capacity': 200, 'speed': 1,
                      'product_capacity': [n * 609, n * 1105, n * 345, n * 32]}  # WDS,ELEC,ED,PNC 50 kg+100kg

VRP = MCVRPTW(Coordinates=Coordinates,Distance=Distance,Travel_time=Traveling_time, Customer_demands=Customer_demands, Vehicle_parameters=Vehicle_parameters,
               Earliest_service_time=Earliest_service_time, Latest_service_time=Latest_service_time,
               Service_time=Service_time,Index_to_id=Index_to_id)
VRP.all_run()
# print(VRP.Distance_between_customers)
# VRP.display_customers()
VRP.display_solution()
# VRP.check_all_is_allright()

if VRP.number_of_vehicle*n/5 == int(VRP.number_of_vehicle*n/5):
    number_of_vehicle = VRP.number_of_vehicle*n/5
else:
    number_of_vehicle = int(VRP.number_of_vehicle * n / 5) +1
print('Values For Ethiopia:')
print('number of vehicle per customer:',n)
print('as the customer demand is to big in comparaison of the capacity of each vehicle, we need to send several vehicles to each customer ')
print('number of total vehicle:',number_of_vehicle)
print('Fixe Cost (cost of the vehicles):',number_of_vehicle*Cost['cost_per_vehicle'])
print('Variable Cost (cost related to the distance):',VRP.traveled_distance*n*Cost['cost_per_km'])
Routes_ordered = []
for r in range(len(VRP.Routes)):
    Routes_ordered.append([Id_to_index[VRP.Routes[r][i]] for i in range(len(VRP.Routes[r]))])
print('route with id from Ethiopya:',Routes_ordered)
print('Arrival time at each cluster of the route:',VRP.Routes_arrival_time)
print('Total Traveled Distance:', VRP.traveled_distance*n)
adapted_capacity = []

for i in VRP.Capacity_per_vehicle:
    table = []
    for j in i:
        table.append(j/n)
    adapted_capacity.append(table)
print('Products Capacity needed by each vehicle:', adapted_capacity)
print('for the PNC, it is an average')
print('Traveled Distance by each vehicle:', VRP.TDistance)