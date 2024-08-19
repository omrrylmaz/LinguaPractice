

import pandas as pd 
import numpy as np 

#gerekli fonksiyonlar
def get_data():
    data = pd.read_csv("data.csv")
    return data