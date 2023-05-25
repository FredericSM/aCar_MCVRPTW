import os
import pandas as pd

def save_history(file_path : str, Data : dict)->None:
    """
    save the history of a computation
    :param file_name:
    :return: None
    """
    if os.path.exists(file_path):
        df = pd.read_csv(file_path,index_col=False)
        Columns_name = list(df.columns)
        df = pd.DataFrame({name: df[name].tolist() + Data[name] for name in Columns_name})
    else:
        df = pd.DataFrame(Data)
        df.to_csv(file_path)


    df.to_csv(file_path, index=False)
