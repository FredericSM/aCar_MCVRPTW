
import pandas as pd
from bs4 import BeautifulSoup as bs
import urllib.request
import re


url = "http://web.cba.neu.edu/~msolomon/r1r2solu.htm"
page=urllib.request.urlopen(url,timeout=5)
soup=bs(page,features="html.parser")
Data = soup.find_all('p', {'class': 'MsoNormal'})

def get_info(string):
    pattern = r'>([^<]+)<'
    result = re.search(pattern, string)
    if result:
        extracted_word = result.group(1)
        return extracted_word
    else:
        print("No match found")

Problem = []
NV = []
Distance = []
Authors = []
index = 1
for i in range(len(Data[1:])):
    data = Data[1:][i].text
    if '\xa0' in data:
        data = data.replace("\xa0", "")
        print(data)
    if index == 1:
        Problem.append(data)
        index += 1
    elif index == 2:
        NV.append(data)
        index += 1
    elif index == 3:
        Distance.append(data)
        index += 1
    else:
        Authors.append(data)
        index=1
print(Problem)
print(NV)
print(Distance)
print(Authors)

Data_for_csv = {
    'Problem':Problem[2:],
    'NV':NV[2:],
    'Distance':Distance[2:],
    'Authors':Authors[2:]
}
df = pd.DataFrame(Data_for_csv)
df.to_csv('solutionR100_200.csv', index=False)




