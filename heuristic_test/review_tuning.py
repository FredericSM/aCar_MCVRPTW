import pandas as pd

Tuning = pd.read_csv('../Dataset/results_heuristic_test/test_tuning.csv')
Solution1 = pd.read_csv('../Dataset/results_heuristic_test/Error.csv')
Error = [(Tuning['distance traveled'][i]-Tuning['Solution'][i])/Tuning['Solution'][i]*100 for i in range(len(Tuning['distance traveled']))]
df_Tuning = pd.DataFrame(Tuning)
df_Tuning['Error'] = Error
df_Tuning_modified = df_Tuning.dropna().tail(df_Tuning.shape[0]-20)
df_Solution1 = pd.DataFrame(Solution1).dropna()
print(df_Tuning_modified)
# print(df_Tuning['Error'].mean())
# print(df_Solution1['Error'].mean())

