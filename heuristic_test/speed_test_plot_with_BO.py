import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import linregress

# %% computation of the average, standart deviation
df = pd.read_csv('speed_test_withBO.csv')
Number_of_customer = [df['Number_of_customers'][i] for i in range(len(df['Number_of_customers']))]
Time_1_products = df['Time_1_products']
# Time_3_products = df['Time_3_products']
# Time_6_products = df['Time_6_products']
Time_10_products = df['Time_10_products']
color = ['b','g','r','y','m','k','c']
Average = []
Standart_deviation = []
Average_minus_Std = []
Average_plus_Std = []

for p in [1,10]:
    Average_bis = []
    Standart_deviation_bis = []
    Average_minus_Std_bis = []
    Average_plus_Std_bis = []

    for i in range(len(Time_1_products)):
        Average_bis.append(np.average(eval(eval('Time_'+str(p)+'_products[i]'))))
        Standart_deviation_bis.append(np.std(eval(eval('Time_'+str(p)+'_products[i]'))))
        Average_minus_Std_bis.append(Average_bis[-1]-Standart_deviation_bis[-1])
        Average_plus_Std_bis.append(Average_bis[-1]+Standart_deviation_bis[-1])
    Average.append(Average_bis)
    Standart_deviation.append(Standart_deviation_bis)
    Average_minus_Std.append(Average_minus_Std_bis)
    Average_plus_Std.append(Average_plus_Std_bis)
# %% plot time according customers
_, ax = plt.subplots()
for j in range(len([1,10])):
    ax.plot(Number_of_customer, Average[j], label=str([1,10][j])+' products',color=color[j])
    ax.plot(Number_of_customer, Average_minus_Std[j],color=color[j],alpha=0.5)
    ax.plot(Number_of_customer, Average_plus_Std[j],color=color[j],alpha=0.5)
    ax.fill_between(Number_of_customer, Average_plus_Std[j],
                    Average_minus_Std[j], facecolor=color[j], alpha=0.2)

ax.set_title('Computing time according to the number of customers')
ax.set_ylabel("Time (s)")
ax.set_xlabel("Number of customers (#)")
ax.legend(loc="upper left")
# plt.draw_if_interactive()
plt.xlim(16, 256)
plt.ylim(0, 400)
plt.show()

# %% Plot log time according customers
_, ax = plt.subplots()
def log_to_list(list):
    return [np.log(list[i]) for i in range(len(list))]
for j in range(len([1,10])):
    ax.plot(Number_of_customer, log_to_list(Average[j]), label=str([1,10][j])+' Products',color=color[j])
    ax.plot(Number_of_customer, log_to_list(Average_minus_Std[j]),color=color[j],alpha=0.5)
    ax.plot(Number_of_customer, log_to_list(Average_plus_Std[j]),color=color[j],alpha=0.5)
    ax.fill_between(log_to_list(Number_of_customer), log_to_list(Average_plus_Std[j]),
                    log_to_list(Average_minus_Std[j]), facecolor=color[j], alpha=0.2)

ax.set_title('Computing time according to the number of customers \n Display in logarithmic scale for the Time')
ax.set_ylabel("Time (ln(s))")
ax.set_xlabel("Number of customers (#)")
ax.legend(loc="upper left")
# plt.draw_if_interactive()
plt.xlim(16, 256)
plt.ylim(3,6)
plt.show()
# %% equation of the line
R_squared = []
Degre = []
_, ax = plt.subplots()
