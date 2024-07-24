import pandas as pd

current_data = pd.DataFrame()

def update_current_data(data):
    global current_data
    current_data = data

def get_current_data():
    global current_data
    return current_data