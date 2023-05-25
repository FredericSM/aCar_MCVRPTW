import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import linregress

# %% computation of the average, standart deviation
df = pd.read_csv('../Dataset/results_heuristic_test/speed_test.csv')
Number_of_customer = [df['Number_of_customers'][i] for i in range(len(df['Number_of_customers']))]
Time_1_products = df['Time_1_products']
Time_3_products = df['Time_3_products']
Time_6_products = df['Time_6_products']
Time_10_products = df['Time_10_products']
color = ['b','g','r','y','m','k','c']
Average = []
Standart_deviation = []
Average_minus_Std = []
Average_plus_Std = []

for p in [1,3,6,10]:
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
for j in range(len([1,3,6,10])):
    ax.plot(Number_of_customer, Average[j], label=str([1,3,6,10][j])+' products',color=color[j])
    ax.plot(Number_of_customer, Average_minus_Std[j],color=color[j],alpha=0.5)
    ax.plot(Number_of_customer, Average_plus_Std[j],color=color[j],alpha=0.5)
    ax.fill_between(Number_of_customer, Average_plus_Std[j],
                    Average_minus_Std[j], facecolor=color[j], alpha=0.2)

ax.set_title('Computing time according to the number of customers')
ax.set_ylabel("Time (s)")
ax.set_xlabel("Number of customers (#)")
ax.legend(loc="upper left")
# plt.draw_if_interactive()
plt.xlim(0, 1024)
plt.ylim(0, 180)
plt.show()
# %% Plot time % products
def change_for_product(list,i):
    return [list[j][i] for j in range(4)]


_, ax = plt.subplots()
for j in range(5):
    ax.plot([1,3,6,10], change_for_product(Average,j), label=str(Number_of_customer[j])+' Customers',color=color[j])
    ax.plot([1,3,6,10], change_for_product(Average_minus_Std,j),color=color[j],alpha=0.5)
    ax.plot([1,3,6,10], change_for_product(Average_plus_Std,j),color=color[j],alpha=0.5)
    ax.fill_between([1,3,6,10], change_for_product(Average_plus_Std,j),
                    change_for_product(Average_minus_Std,j), facecolor=color[j], alpha=0.2)

ax.set_title('Computing time according to the number of products')
ax.set_ylabel("Time (s)")
ax.set_xticks([1,3,6,10])
ax.set_xlabel("Number of products (#)")
ax.legend(loc="upper left")
# plt.draw_if_interactive()
plt.xlim(1, 10)
plt.ylim(0, 4)
plt.show()
_, ax = plt.subplots()
for j in range(5,7):
    ax.plot([1,3,6,10], change_for_product(Average,j), label=str(Number_of_customer[j])+' Customers',color=color[j-5])
    ax.plot([1,3,6,10], change_for_product(Average_minus_Std,j),color=color[j-5],alpha=0.5)
    ax.plot([1,3,6,10], change_for_product(Average_plus_Std,j),color=color[j-5],alpha=0.5)
    ax.fill_between([1,3,6,10], change_for_product(Average_plus_Std,j),
                    change_for_product(Average_minus_Std,j), facecolor=color[j-5], alpha=0.2)

ax.set_title('Computing time according to the number of products')
ax.set_ylabel("Time (s)")
ax.set_xlabel("Number of products (#)")
ax.set_xticks([1,3,6,10])
ax.legend(loc="upper left")
# plt.draw_if_interactive()
plt.xlim(1, 10)
plt.ylim(0, 180)
plt.show()

# %% Plot log time according customers
_, ax = plt.subplots()
def log_to_list(list):
    return [np.log(list[i]) for i in range(len(list))]
for j in range(len([1,3,6,10])):
    ax.plot(log_to_list(Number_of_customer), log_to_list(Average[j]), label=str([1,3,6,10][j])+' Products',color=color[j])
    ax.plot(log_to_list(Number_of_customer), log_to_list(Average_minus_Std[j]),color=color[j],alpha=0.5)
    ax.plot(log_to_list(Number_of_customer), log_to_list(Average_plus_Std[j]),color=color[j],alpha=0.5)
    ax.fill_between(log_to_list(Number_of_customer), log_to_list(Average_plus_Std[j]),
                    log_to_list(Average_minus_Std[j]), facecolor=color[j], alpha=0.2)

ax.set_title('Computing time according to the number of customers \n Display in logarithmic scale')
ax.set_ylabel("Time (ln(s))")
ax.set_xlabel("Number of customers (ln(#))")
ax.legend(loc="upper left")
# plt.draw_if_interactive()
# plt.xlim(0, 7)
# plt.ylim(0, 5)
plt.show()
# %% equation of the line
R_squared = []
Degre = []
_, ax = plt.subplots()
for i in range(4):
    # Fit a linear regression line to the data using numpy's polyfit function
    x = log_to_list(Number_of_customer)
    y = log_to_list(Average[i])
    slope, intercept, r_value, p_value, std_err = linregress(x, y)
    R_squared.append(r_value ** 2)
    Degre.append(slope)

    # Plot the data points and the regression line
    plt.plot(x, y, 'o', label='Data points for '+str([1,3,6,10][i])+' product(s)')
    plt.plot(x, slope * np.array(x) + intercept, label='Regression line')

# Add a title and legend to the plot
plt.title('Linear Regression')
plt.legend()

# Show the plot
plt.show()

# Print the slope and intercept of the regression line
print(R_squared,Degre)

# %% Plot time % products uniformed

def change_for_product_uniformed(list,i):
    return [list[j][i]/Average[-1][i] for j in range(4)]
_, ax = plt.subplots()
for j in range(7):
    print(change_for_product_uniformed(Average,j))
    ax.plot([1,3,6,10], change_for_product_uniformed(Average,j), label=str(Number_of_customer[j])+' Customers',color=color[j])
    ax.plot([1,3,6,10], change_for_product_uniformed(Average_minus_Std,j),color=color[j],alpha=0.5)
    ax.plot([1,3,6,10], change_for_product_uniformed(Average_plus_Std,j),color=color[j],alpha=0.5)
    ax.fill_between([1,3,6,10], change_for_product_uniformed(Average_plus_Std,j),
                    change_for_product_uniformed(Average_minus_Std,j), facecolor=color[j], alpha=0.2)


ax.set_title('Standardized Computing time according to the number of products')
ax.set_ylabel("Standardized Time (s)")
ax.set_xticks([1,3,6,10])
ax.set_xlabel("Number of products (#)")
ax.legend(loc="upper left")
# plt.draw_if_interactive()
plt.xlim(1, 10)
plt.ylim(0, 2)
plt.show()
