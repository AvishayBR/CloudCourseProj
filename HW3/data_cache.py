import pandas as pd

# Define a global variable to store the current data
current_data = pd.DataFrame()

# Define a global variable to store the current patterns
def update_current_data(data):
    global current_data
    current_data = data

# Define a function to get the current data
def get_current_data():
    global current_data
    return current_data