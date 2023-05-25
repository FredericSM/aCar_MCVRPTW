
import pandas as pd
from bs4 import BeautifulSoup as bs
import urllib.request
import re


url = "http://web.cba.neu.edu/~msolomon/r101.htm"
page=urllib.request.urlopen(url,timeout=5)
soup=bs(page,features="html.parser")
Name1= soup.find_all('font',{'color': '#FF0000'})
Name2= soup.find_all('font',{'color': '#FF6666'})
Name = Name1+Name2
Columns_name = soup.find_all('font',{'color': '#000099'})
Data = soup.find_all('font',{'color': '#3366FF'})
Data_modified = Data[1:]
Data_modified[0]=Data_modified[1]
number_of_set = int(len(Data)/100)

def get_number(string):
    pattern = r'(\d+\.\d+)'
    match = re.search(pattern, string)
    if match:
        return float(match.group(1))
    else:
        print("No match found")

def get_name(string):
    pattern = r'([A-Z]+\d+)'
    match = re.search(pattern, string)
    if match:
        return match.group(1)
    else:
        print("No match found")

def get_capacity(string):
    match = re.search(r'>([\d,]+)<', string)
    if match:
        number = int(match.group(1).replace(',', ''))
        return number
    else:
        print("No number found in the input string.")

for iteration in range(number_of_set):
    #Coordinates = {i%101: (float(str(Data_modified[i]).split()[3]),float(str(Data_modified[i]).split()[4])) for i in range(iteration*101,101+iteration*101)}
    Coordinates = [(float(str(Data_modified[i]).split()[3]),float(str(Data_modified[i]).split()[4])) for i in range(iteration*101,101+iteration*101)]+[None]
    #Customer_demand = {i%101: [float(str(Data_modified[i]).split()[5])] for i in range(iteration*101+1,101+iteration*101)}
    Customer_demand =[[float(str(Data_modified[i]).split()[5])] for i in range(iteration*101,101+iteration*101)]+[None]
    Earliest_service_time = [[float(str(Data_modified[i]).split()[6])] for i in range(iteration*101,101+iteration*101)] + [max([[float(str(Data_modified[i]).split()[7])] for i in range(iteration*101,101+iteration*101)])]
    Latest_service_time = [[float(str(Data_modified[i]).split()[7])] for i in range(iteration*101,101+iteration*101)] + [max([[float(str(Data_modified[i]).split()[7])] for i in range(iteration*101,101+iteration*101)])]
    #Service_time = {i%101: get_number(str(Data_modified[i]).split()[8]) for i in range(iteration*101+1,101+iteration*101)}
    Service_time =[get_number(str(Data_modified[i]).split()[8]) for i in range(iteration*101,101+iteration*101)]+[None]
    #Vehicle_capacity = [get_capacity(str(Data[0]).split()[1])] + [None for i in range(101)]
    Vehicle_capacity = [200] + [None for i in range(101)]
    Data_for_csv = {
        'Coordinates':Coordinates,
        'Customer_demands':Customer_demand,
        'Earliest_service_time':Earliest_service_time,
        'Latest_service_time':Latest_service_time,
        'Service_time':Service_time,
        'Vehicle_capacity':Vehicle_capacity
    }
    df = pd.DataFrame(Data_for_csv)
    df.to_csv('dataset'+get_name(str(Name[1+iteration]).split()[2])+'.csv', index=False)
