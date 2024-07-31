import pandas as pd
import sys
import plotly.express as px
from dash import Dash, dcc, html, Input, Output, State
import dash_bootstrap_components as dbc
from pyngrok import ngrok
import requests
import base64
import io
import datetime
import plotly.graph_objects as go
from firebase import firebase
import firebase_admin
from firebase_admin import credentials, storage
import json
from nltk.stem import PorterStemmer
import requests
from bs4 import BeautifulSoup
import re
pd.options.mode.chained_assignment = None
def total_interactions(data):
    return len(data)

def count_interactions_by_type(data):
    return data['Description'].value_counts()

def interactions_over_time(data, interval='h'):  # Updated 'H' to 'h'
    data.loc[:,'Time'] = pd.to_datetime(data['Time'])
    return data.set_index('Time').resample(interval)['Description'].count()

def interactions_by_user(data):
    return data['User'].value_counts()

def session_durations(data):
    data['Time'] = pd.to_datetime(data['Time'])
    data = data.sort_values(by=['User', 'Time'])
    sessions = data[data['Description'].str.contains('Open document|Close document')].copy()
    sessions['Next_Time'] = sessions['Time'].shift(-1)
    sessions['Next_User'] = sessions['User'].shift(-1)
    sessions = sessions[
        (sessions['Description'].str.contains('Open document')) & (sessions['User'] == sessions['Next_User'])]
    sessions['Session_Duration'] = sessions['Next_Time'] - sessions['Time']
    return sessions[['User', 'Time', 'Next_Time', 'Session_Duration']]

def interactions_by_time_of_day(data):
    data.loc[:,'Time'] = pd.to_datetime(data.loc[:,'Time'])
    data.loc[:,'Hour'] = data.loc[:,'Time'].dt.hour
    return data.groupby('Hour')['Description'].count()

def top_performers(data):
    data = data.drop(columns=['Time', 'Document','Tab'])
    unique_students = data['User'].unique().tolist()
    students_iterations = dict()
    for student in unique_students:
        student_data = data[data['User'] == student]
        delete_count = student_data['Description'].str.contains('Delete').sum()
        total_rows = len(student_data)
        ratio = 100 - (delete_count / total_rows) * 100
        students_iterations[student] = ratio
    return students_iterations
def get_users_adding_interations(data):
    data = data.drop(columns=['Time', 'Document','Tab'])
    unique_students = data['User'].unique().tolist()
    students_iterations = dict()
    for student in unique_students:
        student_data = data[data['User'] == student]
        add_count = 0
        add_count = add_count + student_data['Description'].str.contains('Create document').sum() * 4
        add_count = add_count + student_data['Description'].str.contains('Add').sum() * 2
        add_count = add_count + student_data['Description'].str.contains('Insert').sum() * 2
        add_count = add_count + student_data['Description'].str.contains('Update').sum() * 1
        add_count = add_count + student_data['Description'].str.contains('Edit').sum() * 1
        add_count = add_count + student_data['Description'].str.contains('Delete').sum() * -2
        add_count = add_count + student_data['Description'].str.contains('Trash').sum() * -4
        students_iterations[student] = add_count
    average = 0
    for student in students_iterations.keys():
        average = average + students_iterations[student]
    average = average / len(students_iterations)
    return students_iterations, average