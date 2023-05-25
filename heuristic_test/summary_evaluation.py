import pandas as pd
import re

with open('../Dataset/results_heuristic_test/Evaluation_with_tuning.csv') as csvfile:
    Data_tuned = pd.read_csv(csvfile)
with open('../Dataset/results_heuristic_test/Evaluation.csv') as csvfile:
    Data = pd.read_csv(csvfile)


Data[['Name', 'Attribut']] = Data['Name of the set'].str.extract(r'([A-Za-z]+)(\d+)', expand=True)
Data = Data.drop('Problems',axis=1)
Data_tuned[['Name', 'Attribut']] = Data_tuned['Name of the set'].str.extract(r'([A-Za-z]+)(\d+)', expand=True)
Pb = 'C'
type = 2
# Name of the set,Number of customer,Lower Bound,NV,SNV,ATD,ETD,Problems
# Name of the set,Number of customer,Lower Bound,NV,SNV,ATD,ETD,Time,HP1,HP2,HP3,HP4
def show(Pb,n,type):
    if type == 1:
        Value = Data[(Data['Number of customer']==n) & (Data['Name']==Pb) & (Data['Attribut']<'200')].sum()
        Value_to_show = Data_tuned[(Data_tuned['Number of customer']==n) & (Data_tuned['Name']==Pb) & (Data_tuned['Attribut']<'200')].sum()
        Time = Data_tuned[(Data_tuned['Number of customer']==n) & (Data_tuned['Name']==Pb) & (Data_tuned['Attribut']<'200')].mean()
        Time = Time[6]
        print('LBNV:',Value_to_show[2],'Gap:',(Value_to_show[5]-Value_to_show[6])/Value_to_show[6]*100,'Gap imp:',(Value[5]-Value_to_show[5])/Value_to_show[5]*100,'Trend:',(Value_to_show[3]-Value_to_show[2])/Value_to_show[2]*100,'Trend sol:',(Value_to_show[4]-Value_to_show[2])/Value_to_show[2]*100,'Trend imp:',(Value[3]-Value_to_show[3])/Value_to_show[3]*100,'Time:',Time)
    else:
        Value = Data[(Data['Number of customer']==n) & (Data['Name']==Pb) & (Data['Attribut']>'200')].sum()
        Value_to_show = Data_tuned[(Data_tuned['Number of customer']==n) & (Data_tuned['Name']==Pb) & (Data_tuned['Attribut']>'200')].sum()
        Time = Data_tuned[(Data_tuned['Number of customer']==n) & (Data_tuned['Name']==Pb) & (Data_tuned['Attribut']>'200')].mean()
        Time = Time[6]
        print('LBNV:',Value_to_show[2],'Gap:',(Value_to_show[5]-Value_to_show[6])/Value_to_show[6]*100,'Gap imp:',(Value[5]-Value_to_show[5])/Value_to_show[5]*100,'Trend:',(Value_to_show[3]-Value_to_show[2])/Value_to_show[2]*100,'Trend sol:',(Value_to_show[4]-Value_to_show[2])/Value_to_show[2]*100,'Trend imp:',(Value[3]-Value_to_show[3])/Value_to_show[3]*100,'Time:',Time)

# show(Pb,25,type)
# show(Pb,50,type)
# show(Pb,100,type)
# Data = Data_tuned
# print('Gap:',(Value[5]-Value[6])/Value[6]*100,'Trend:',(Value[3]-Value[2])/Value[2]*100,'Trend_sol:',(Value[4]-Value[2])/Value[2]*100)
Value = Data[(Data['Name']=='R')].sum()
print((Value[5]-Value[6])/Value[6]*100,(Value[3]-Value[2])/Value[2]*100,(Value[4]-Value[2])/Value[2]*100)
Value = Data[(Data['Name']=='RC')].sum()
print((Value[5]-Value[6])/Value[6]*100,(Value[3]-Value[2])/Value[2]*100,(Value[4]-Value[2])/Value[2]*100)
Value = Data[(Data['Name']=='C')].sum()
print((Value[5]-Value[6])/Value[6]*100,(Value[3]-Value[2])/Value[2]*100,(Value[4]-Value[2])/Value[2]*100)

Value = Data[(Data['Attribut']<'200')].sum()
print((Value[5]-Value[6])/Value[6]*100,(Value[3]-Value[2])/Value[2]*100,(Value[4]-Value[2])/Value[2]*100)
Value = Data[(Data['Attribut']>'200')].sum()
print((Value[5]-Value[6])/Value[6]*100,(Value[3]-Value[2])/Value[2]*100,(Value[4]-Value[2])/Value[2]*100)

Value = Data[(Data['Number of customer']==25)].sum()
print((Value[5]-Value[6])/Value[6]*100,(Value[3]-Value[2])/Value[2]*100,(Value[4]-Value[2])/Value[2]*100)
Value = Data[(Data['Number of customer']==50)].sum()
print((Value[5]-Value[6])/Value[6]*100,(Value[3]-Value[2])/Value[2]*100,(Value[4]-Value[2])/Value[2]*100)
Value = Data[(Data['Number of customer']==100)].sum()
print((Value[5]-Value[6])/Value[6]*100,(Value[3]-Value[2])/Value[2]*100,(Value[4]-Value[2])/Value[2]*100)




