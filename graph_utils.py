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





def total_interactions(data):
    return len(data)


def count_interactions_by_type(data):
    return data['Description'].value_counts()


def interactions_over_time(data, interval='H'):
    data['Time'] = pd.to_datetime(data['Time'])
    return data.set_index('Time').resample(interval)['Description'].count()


def interactions_by_user(data):
    return data['User'].value_counts()


def session_durations(data):
    data['Time'] = pd.to_datetime(data['Time'])
    data = data.sort_values(by=['User', 'Time'])
    sessions = data[data['Description'].str.contains('Open document|Close document')]
    sessions['Next_Time'] = sessions['Time'].shift(-1)
    sessions['Next_User'] = sessions['User'].shift(-1)
    sessions = sessions[
        (sessions['Description'].str.contains('Open document')) & (sessions['User'] == sessions['Next_User'])]
    sessions['Session_Duration'] = sessions['Next_Time'] - sessions['Time']
    return sessions[['User', 'Time', 'Next_Time', 'Session_Duration']]


def interactions_by_time_of_day(data):
    data['Time'] = pd.to_datetime(data['Time'])
    data['Hour'] = data['Time'].dt.hour
    return data.groupby('Hour')['Description'].count()
