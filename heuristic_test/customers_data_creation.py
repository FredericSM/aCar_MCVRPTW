
import pandas as pd
import random as rnd

Coordinates_set=[]
Customer_demands_1_set=[]
Customer_demands_3_set=[]
Customer_demands_6_set=[]
Customer_demands_10_set=[]
Earliest_service_time_set=[]
Latest_service_time_set=[]

for i in range(50):
    n = 1024
    Coordinates = {i: (rnd.randint(-20, 20), rnd.randint(-20, 20)) for i in range(n + 1)}
    Earliest_service_time = [0] + [rnd.randint(0, 850) for i in range(n)] + [0]
    Latest_service_time = [1000] + [Earliest_service_time[i + 1] + rnd.randint(50, 150) for i in range(n)] + [1000]
    Coordinates_set.append(Coordinates)
    Earliest_service_time_set.append(Earliest_service_time)
    Latest_service_time_set.append(Latest_service_time)
    for p in [1,3,6,10]:
        Customer_demands = {i: [rnd.choices([0, 1], weights=[0.2, 0.8], k=1)[0] * rnd.randint(0, 10) for product in range(p)] for i in
                            range(1, n + 1)}
        Customer_demands[0] = [0 for i in range(p)]
        eval('Customer_demands_'+str(p)+'_set').append(Customer_demands)

Data_for_csv = {
    'Coordinates_set':Coordinates_set,
    'Earliest_service_time_set':Earliest_service_time_set,
    'Latest_service_time_set':Latest_service_time_set,
    'Customer_demands_p1_set':Customer_demands_1_set,
    'Customer_demands_p3_set':Customer_demands_3_set,
    'Customer_demands_p6_set':Customer_demands_6_set,
    'Customer_demands_p10_set':Customer_demands_10_set,
}
df = pd.DataFrame(Data_for_csv)
df.to_csv('50_customers_data.csv',index=True)