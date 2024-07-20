import pandas as pd
import sys
print(sys.executable)
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

# ************* indexing functions *************
def fetch_page(url):
    response = requests.get(url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        return soup
    else:
        return None


def index_words(soup):
    index = {}
    words = re.findall(r'\w+', soup.get_text())
    for word in words:
        word = word.lower()
        if word in index:
            index[word] += 1
        else:
            index[word] = 1
    return index

def remove_stop_words(index):
    stop_words = {'a', 'an', 'the', 'and', 'or', 'in', 'on', 'at', 'to'}
    for stop_word in stop_words:
        if stop_word in index:
            del index[stop_word]
    return index

def apply_stemming(index):
    stemmer = PorterStemmer()
    stemmed_index = {}
    for word, count in index.items():
        stemmed_word = stemmer.stem(word)
        if stemmed_word in stemmed_index:
            stemmed_index[stemmed_word] += count
        else:
            stemmed_index[stemmed_word] = count
    return stemmed_index
    
def search(query, index):
    stemmer = PorterStemmer()
    query_words = re.findall(r'\w+', query.lower())
    results = {}
    for word in query_words:
        word = stemmer.stem(word)
        if word in index:
            results[word] = index[word]
        else:
          results[word] = 0
    return results

def search_engine(url, query):
    soup = fetch_page(url)
    if soup is None:
        return None
    index = index_words(soup)
    index = remove_stop_words(index)
    index = apply_stemming(index)
    results = search(query, index)
    return results

# ************* end indexing functions *************




# ************* uncomment this object when trying to run the app *************
# ************* comment the object when trying to push for github *************

# access_info = {
#   "type": "service_account",
#   "project_id": "cloudproject-5451f",
#   "private_key_id": "fdec51fa9f9468330cd3128cbcb78075f1c933eb",
#   "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQC0k/PKnsSM2Bn2\nmTftVYXqiXm55vNc1jdrCSw7A5tu9RKdKWwLYRgBMXRgvO6FT1pRK4YIiXTxQqDc\n7RUZ6Xez/hUm4sPu9NjzWxNjRpByHAWzLNMSd39XNHDDE2g8WAuN1GYRLbwbFXtx\nh3fexoSfIKJhT2EFxc8rkarmH3c0f+Di+G38Z2WsUl3tiw/yg5yQMwhyti5X1ORS\nCbrw4B24+tokv3MsRQa3FTS273vXNvivA7e+nq5C/eUAkvNjBiEujP8xfc0We4YR\nC0wPBfee9Irv6eLJFcDCwjHM93COu57MVwdEwHC0DESp9ma1z83vdroTgMBFJs1M\nyontyhMlAgMBAAECggEABJQgXKCTFqza6WN9vBtjmd7LosQ2EJ2wKgjmE+tFx/FO\n14Qp7btdFQYXawo6wgaRDx3SQVdxwexHtZt7BqG990Jg3cb5B7PEejBOIh0hEQzE\n2DrD31G2D7kiYs/dcnNkfC1Izc/YxSlRtazuOt6tuZsuy/sis8mgNNhRQ9tWGm6h\n05B/0Dhy7G5//efXfuvyu61Od3NsCbVuRce5vmOWu0lvw22sTcGJtmrtVYkQZU0C\nTap+5rbuDaZIZ06ruweIcwB/luU1ruQL1zKiCcVOa/8qXtBKAjnkdi+TOtTcUuMG\nSDV4o/NQUd1yKTy3JldNgDOi8O8j8w3+TubnCVRkAQKBgQDsbLdqkkSueSCCh906\n0OLFJkkrt1YepVp/OIfw70aWpkHHuWDJtH4BlEZkEY/NIhKakgJReSzbAqNt9ZY/\n+KJMAAczMsTgFMid98a7ielzO/vUxLDVDXaEsndOAPfv43X0kNldgioU0RPx10gk\n5j0ucQ6ikYCrBD+PxwoneNeXUQKBgQDDh4CUu/dFaeh11SeK2I763FmvoWDur8lz\nkhGIRZ65meptwKDncWtfHM+lQzMatj8Du0D1wTN3siDW14rYp9zISl8D5r4H11pG\n2cRfxohqeu+htFIaufbxDCY53+EsX0/fbzRJ7+5wN3lJscDcRy8VAZOfyHVLfu5s\n1ZZFMbCxlQKBgDvGuREu7kKWyYt3Qo4uZkemiHWPIy0Ybasg5e4a8WQBoTwYOMqG\n4h0QGkQO1Kbu6HlAVWm4E4lEP4H7yANgn9hLYYamXXSyjI60KQEdu3KxRdjj6jnT\n75VZciS8xfNXNWmiffLQiEc/HaXV4p3BwNJPL34W/8s9hbyafIzCVvAhAoGAO8lH\n+LKMxi2/BaCaiarz9SLBTaGTqQgZGfx03e0jvm6grtRynrIgeaGuoEKu8qD9HZ/5\nGevsV9IglnCrpNmW+as76E56lp0znmxhzkM/XQegFBq17DQmnMfxPEsHZ/Dw1EoF\nfAIgLzHXJUBzzyb473xe7kF2FBKIxsB8RUYPWA0CgYEAiS21GsctCmKQwIMwRvY1\nMPSFVyfTomwXmXQPWEAIrbRsIJsGe3SnR3fukX9LMHAi5NAtMRp+cGMRO/onWUCM\nyNz7XIXXZXfhuGCKngfMYf3ubPuk9JmuxONNDN6ebLNWy+PcWyVdg8jFvIeTFyFp\nGGjGqDCAEvUP3b45wh3ItKI=\n-----END PRIVATE KEY-----\n",
#   "client_email": "firebase-adminsdk-ze21r@cloudproject-5451f.iam.gserviceaccount.com",
#   "client_id": "113989524318945156419",
#   "auth_uri": "https://accounts.google.com/o/oauth2/auth",
#   "token_uri": "https://oauth2.googleapis.com/token",
#   "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
#   "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/firebase-adminsdk-ze21r%40cloudproject-5451f.iam.gserviceaccount.com",
#   "universe_domain": "googleapis.com"
# }

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


def home_page():
    return html.Div([
        html.H1("Home Page"),
        html.P("Welcome to the OnShape Analysis Tool."),
        html.P(
            "This application is designed to help managers of OnShape crews analyze and monitor the work of their team."),
        html.P(
            "By processing log files in JSON format from the OnShape application, this tool provides detailed statistics and insights into team performance, project progress, and collaboration efficiency."),
        html.P("Navigate to the Dashboard to see detailed visualizations and analysis."),
        html.Div(
            [
                html.Img(
                    src="https://cdn.sanity.io/images/tlr8oxjg/production/22c3b048689e6b8cd048157c7eb3c01cce769a41-1456x816.png",
                    className="image-3d"),
                html.Img(src="https://www.netscribes.com/wp-content/uploads/2023/01/Innovation-strategies.jpg",
                         className="image-3d"),
                html.Img(
                    src="https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSfxTS5KrMzEwuG9QqZlNrJYB7Gfp7NdJAR4g&s",
                    className="image-3d"),
            ],
            style={"display": "flex", "justify-content": "space-around", "margin-top": "40px"}
        )
    ], className="home-page")


# Function to upload file to Firebase Storage
def upload_to_firebase(filename, content):
    bucket = storage.bucket()
    blob = bucket.blob(filename)
    blob.upload_from_string(content)
    return blob.public_url

# Function to get files from Firebase Storage
def get_files_from_firebase():
    bucket = storage.bucket()
    blobs = bucket.list_blobs()
    files = [blob.name for blob in blobs]
    return files

# Function to download file from Firebase Storage
def download_from_firebase(filename):
    bucket = storage.bucket()
    blob = bucket.blob(filename)
    content = blob.download_as_text()
    return content

def setup_page():
    return html.Div([
      html.Div([
        html.H1("Data Setup"),
        dcc.Upload(
            id='upload-data',
            children=html.Div([
                'Drag and Drop or ',
                html.A('Select a JSON File')
            ]),
            style={"display": "flex", "justify-content": "space-around", "margin-top": "40px"},
            multiple=False
        ),
        html.Div(id='output-data-upload'),
        html.Button("Save", id="save-button", n_clicks=0,
                    style={"display": "none", "margin": "auto", "margin-top": "20px"}, className="setup-button"),
        html.Div(id='save-state', style={"margin": "auto", "margin-top": "20px"}),
    ], className="setup-page"),
    html.Div([
      html.H1("Search For A File"),
      html.Button("Search", id="search-button", n_clicks=0,
                  style={"margin": "auto", "margin-top": "20px"}, className="setup-button"),
      dcc.Dropdown(id='file-dropdown', style={"display": "none", "margin": "auto", "margin-top": "20px"}),
      html.Div(id='output-search-state'),
      html.Div(id='output-analysis', style={"display": "none"}),
    ], className="setup-page", style={"margin-top": "20px"})
    ], className="setup-container")


def analysis_page():
    return html.Div([
        html.H1("Analysis & Statistics"),
        html.P("Select documents to filter the data:"),
        dcc.Dropdown(
            id='document-dropdown',
            options=[{'label': doc, 'value': doc} for doc in current_data['Document'].unique() if
                     not doc is None and not doc == ""],
            multi=True
        ),
        html.Button("Generate", id='generate-button', n_clicks=0, className="button-generate"),
        html.Div(id='filtered-data-output')
    ], className="analysis-page")


def additional_page_2():
    return html.Div([
        html.H1("Additional Page 2"),
        html.P("This is the additional page 2.")
    ])

def page_index():
    return html.Div([
        html.H1("OnShape Glossary Index"),
        html.H4("Insert your parameters in order to view frequency of words in the Glossary"),
        dcc.Input(id='text-input', type='text', placeholder='Enter parameters here', style={"margin": "10px"}),
        html.Button('Submit', id='submit-button', n_clicks=0, style={"margin": "10px"}, className="setup-button"),
        html.Div(id='output-container', style={"margin-top": "20px"}),
        html.Div(id='output-data-index'),
        html.Div(id='index-state-table', style={"margin": "auto", "margin-top": "20px"}),
    ], className="setup-page")


def about_page():
    return html.Div([
        html.H1("About Page"),
        html.P("Welcome to the About page of our application."),
        html.P("This application is designed to analyze and monitor the work of OnShape teams."),
        html.P(
            "It processes log files in JSON format to provide insights into team performance, project progress, and collaboration efficiency."),
        html.P("Navigate through the different pages to explore visualizations and detailed statistics.")
    ], style={'padding': '20px'}, className="setup-page")


# Initialize the Dash app
app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
current_data = pd.DataFrame()
# Define the sidebar
sidebar = html.Div(
    [
        html.Div(
            [
                html.Img(
                    src="https://play-lh.googleusercontent.com/yAS9WJJnjlCx77RxIvJSssrixhCdUxnBlM3CuPnQpl8QI3Ez19KreBL4xREc1gtmK_Y",
                    style={"height": "65px", "margin-right": "10px"}),  # Adjust the URL and style as needed
                html.H2("OnShape Analysis", className="display-10",
                        style={"color": "white", "display": "inline-block", "vertical-align": "middle"})
            ],
            style={"display": "flex", "align-items": "center"}
        ),
        html.Hr(),
        dbc.Nav(
            id='sidebar-nav',
            children=[
                dbc.NavLink("Home", href="/", active="exact", className="nav-link"),
                dbc.NavLink("Setup", href="/setup", active="exact", className="nav-link"),
                dbc.NavLink("Glossary Index", href="/index", active="exact", className="nav-link"),
                dbc.NavLink("About", href="/about", active="exact", className="nav-link"),
            ],
            vertical=True,
            pills=True,
        ),
        # Hidden div to store the file upload state
        html.Div(id='upload-state', style={'display': 'none'}),
    ],
    className="sidebar"
)

# Define the content layout
content = html.Div(id="page-content", className="page-content")

# Define the app layout
app.layout = html.Div([
    dcc.Location(id="url"),
    sidebar,
    content
])


# Define the callback to update the page content based on the URL
@app.callback(Output("page-content", "children"), [Input("url", "pathname")])
def render_page_content(pathname):
    if pathname == "/":
        return home_page()
    elif pathname == "/setup":
        return setup_page()
    elif pathname == "/about":
        return about_page()
    elif pathname == "/analysis":
        return analysis_page()
    elif pathname == "/additional-page-2":
        return additional_page_2()
    elif pathname == "/index":
        return page_index()
    else:
        return html.Div([
            html.H1("404: Not found"),
            html.P("The requested page was not found.")
        ])


@app.callback(
    [Output('output-container', 'children'),
    Output('index-state-table', 'children')],
    Input('submit-button', 'n_clicks'),
    State('text-input', 'value')
)
def update_glossary_index(n_clicks, value):
    glossary_url = 'https://cad.onshape.com/help/Content/Glossary/glossary.htm'
    if n_clicks > 0:
      if not value:
        return 'Cannot index an empty input', ''
      else:
        result = search_engine(glossary_url, value)
        if not result:
          return f'Cannot find any index related to {value}', ''
        
        keys = list(result.keys())
        values = list(result.values())



        table = go.Figure(data=[go.Table(
        header=dict(values=['term', 'frequency'],
                    fill_color='paleturquoise',
                    align='left'),
        cells=dict(values=[keys, values],
                   fill_color='lavender',
                   align='left'))
        ])
        return '', html.Div([
                    html.H5("The results"),
                    dcc.Graph(
                        id='table-index',
                        figure=table
                    )
                ])
    return '', ''

# Callback to handle file upload and convert JSON to DataFrame
@app.callback(
    [Output('output-data-upload', 'children'),
     Output('upload-state', 'children')],
    [Input('upload-data', 'contents')],
    [State('upload-data', 'filename'),
     State('upload-data', 'last_modified')]
)
def update_output(content, filename, date):
    global current_data
    if content is not None:
        content_type, content_string = content.split(',')
        decoded = base64.b64decode(content_string)
        try:
            if '.json' in filename:
                # Assume that the user uploaded a JSON file
                data = pd.read_json(io.StringIO(decoded.decode('utf-8')))
                current_data = data
                table = go.Figure(data=[go.Table(
                    header=dict(values=list(data.columns),
                                fill_color='paleturquoise',
                                align='left'),
                    cells=dict(values=[data[col] for col in data.columns],
                               fill_color='lavender',
                               align='left'))
                ])
                return html.Div([
                    html.H5(filename),
                    html.H6(datetime.datetime.fromtimestamp(date)),
                    dcc.Graph(
                        id='table-graph',
                        figure=table
                    )
                ]), 'uploaded'
            else:
                return html.Div([
                'Must upload a file with format .json only'
            ]), ''
        except Exception as e:
            print(e)
            return html.Div([
                'There was an error processing this file.'
            ]), ''
    return html.Div(), ''


@app.callback(
    Output('save-button', 'style'),
    [Input('upload-state', 'children')]
)
def show_save_button(upload_state):
    if upload_state == 'uploaded':
        return {"display": "block", "margin": "auto", "margin-top": "20px"}
    return {"display": "none"}


@app.callback(
    Output('file-dropdown', 'options'),
    Output('file-dropdown', 'style'),
    Input('search-button', 'n_clicks')
)
def update_dropdown(n_clicks):
    if n_clicks > 0:
        files = get_files_from_firebase()
        options = [{'label': file, 'value': file} for file in files]
        return options, {"margin": "auto", "margin-top": "20px", "display": "block"}
    return [], {"display": "none"}

@app.callback(
    Output('save-state', 'children'),
    [Input('save-button', 'n_clicks')],
    [State('upload-data', 'contents'),
     State('upload-data', 'filename')]
)
def save_to_firebase(n_clicks, content, filename):
    if n_clicks > 0 and content is not None:
        content_type, content_string = content.split(',')
        decoded = base64.b64decode(content_string)
        try:
            if '.json' in filename:
                new_data = json.loads(decoded.decode('utf-8'))
                # Fetch existing data from Firebase
                existing_data = FBconn.get('/shablool/', None)
                # Handle case where existing_data is None
                if existing_data is None:
                    FBconn.post('/shablool/', new_data)
                    data_url = upload_to_firebase(filename, decoded)
                # Check if new data is already in the database
                elif new_data not in existing_data.values():
                    # Post to Firebase
                    FBconn.post('/shablool/', new_data)
                    data_url = upload_to_firebase(filename, decoded)
                else:
                    return 'Data already exists in the database'
                return 'Data saved successfully'
        except Exception as e:
            print(e)
            return 'Error saving data'
    return ''

@app.callback(
    [Output('output-search-state', 'children'),
    Output('output-analysis','children')],
    Input('file-dropdown', 'value')
)
def display_file(filename):
    global current_data
    if filename:
        content = download_from_firebase(filename)
        data = pd.read_json(io.StringIO(content))
        current_data = data
        table = go.Figure(data=[go.Table(
            header=dict(values=list(data.columns),
                        fill_color='paleturquoise',
                        align='left'),
            cells=dict(values=[data[col].tolist() for col in data.columns],
                       fill_color='lavender',
                       align='left'))
        ])
        
        return dcc.Graph(figure=table), 'uploaded'
    return html.Div(), ''

# Callback to update the sidebar dynamically based on the file upload state
@app.callback(
    Output('sidebar-nav', 'children'),
    [Input('upload-state', 'children'),
    Input('output-analysis', 'children')]
)
def update_sidebar(upload_state, output_analysis):
    nav_links = [
        dbc.NavLink("Home", href="/", active="exact", className="nav-link"),
        dbc.NavLink("Setup", href="/setup", active="exact", className="nav-link"),

    ]
    if (upload_state == 'uploaded' or output_analysis == 'uploaded'):
        nav_links.extend([
            dbc.NavLink("Analysis & Statistics", href="/analysis", active="exact", className="nav-link"),
            dbc.NavLink("Additional Page 2", href="/additional-page-2", active="exact", className="nav-link"),
            dbc.NavLink("Glossary Index", href="/index", active="exact", className="nav-link"),
            dbc.NavLink("About", href="/about", active="exact", className="nav-link")
        ])
    else:
        nav_links.extend([
            dbc.NavLink("Glossary Index", href="/index", active="exact", className="nav-link"),
            dbc.NavLink("About", href="/about", active="exact", className="nav-link")
        ])
    return nav_links


@app.callback(
    Output('filtered-data-output', 'children'),
    [Input('generate-button', 'n_clicks')],
    [State('document-dropdown', 'value')]
)
def generate_graph(n_clicks, selected_documents):
    if n_clicks > 0 and selected_documents:
        global current_data
        filtered_data = current_data[current_data['Document'].isin(selected_documents)]
        if not filtered_data.empty:
            # Ensure 'Time' is in datetime format
            filtered_data['Time'] = pd.to_datetime(filtered_data['Time'])

            # Calculate the time difference between consecutive entries for each user
            filtered_data = filtered_data.sort_values(by=['User', 'Time'])
            filtered_data['Time_Diff'] = filtered_data.groupby('User')['Time'].diff().fillna(pd.Timedelta(seconds=0))

            # Convert 'Time_Diff' to total seconds
            filtered_data['Time_Spent'] = filtered_data['Time_Diff'].dt.total_seconds()

            # Summarize the time spent by each user for each document
            user_document_time_spent = filtered_data.groupby(['User', 'Document'])['Time_Spent'].sum().reset_index()
            user_document_time_spent['Time_Spent_hours'] = user_document_time_spent['Time_Spent'] / 3600

            # Create the bar chart for time spent by each user on each document
            time_spent_fig = px.bar(user_document_time_spent, x='User', y='Time_Spent_hours', color='Document',
                                    labels={'Time_Spent_hours': 'Time Spent (hours)'},
                                    title='Time Spent by Each User on Each Document',
                                    barmode='group')

            # Generate other required plots
            total_interactions_fig = go.Figure(go.Indicator(
                mode="number",
                value=total_interactions(filtered_data),
                title={"text": "Total Interactions"}
            ))

            interactions_by_type_counts = count_interactions_by_type(filtered_data)
            interactions_by_type_fig = px.bar(interactions_by_type_counts, x=interactions_by_type_counts.index,
                                              y=interactions_by_type_counts.values,
                                              labels={'index': 'Interaction Type', 'y': 'Count'},
                                              title='Interactions by Type')

            interactions_over_time_counts = interactions_over_time(filtered_data)
            interactions_over_time_fig = px.line(interactions_over_time_counts, x=interactions_over_time_counts.index,
                                                 y=interactions_over_time_counts.values,
                                                 labels={'index': 'Time', 'y': 'Count'}, title='Interactions Over Time')

            interactions_by_user_counts = interactions_by_user(filtered_data)
            interactions_by_user_fig = px.bar(interactions_by_user_counts, x=interactions_by_user_counts.index,
                                              y=interactions_by_user_counts.values,
                                              labels={'index': 'User', 'y': 'Count'}, title='Interactions by User')

            interactions_by_time_of_day_counts = interactions_by_time_of_day(filtered_data)
            interactions_by_time_of_day_fig = px.bar(interactions_by_time_of_day_counts,
                                                     x=interactions_by_time_of_day_counts.index,
                                                     y=interactions_by_time_of_day_counts.values,
                                                     labels={'index': 'Hour of Day', 'y': 'Count'},
                                                     title='Interactions by Time of Day')

            return html.Div([
                dcc.Graph(figure=total_interactions_fig),
                dcc.Graph(figure=interactions_by_type_fig),
                dcc.Graph(figure=interactions_over_time_fig),
                dcc.Graph(figure=interactions_by_user_fig),
                dcc.Graph(figure=interactions_by_time_of_day_fig),
                dcc.Graph(figure=time_spent_fig)
            ])
    return html.Div("No data selected or no data available for the selected documents.")


# Get your ngrok authtoken from https://dashboard.ngrok.com/get-started/your-authtoken
NGROK_AUTH_TOKEN = '2jBmzuJoeRViFBXDX6EoozJkJ0w_5SyaeULeLKBpARpvbw48X'
ngrok.set_auth_token(NGROK_AUTH_TOKEN)

# Run the app with ngrok
if __name__ == '__main__':
    # Connect to Firebase
    FBconn = firebase.FirebaseApplication('https://cloudproject-5451f-default-rtdb.europe-west1.firebasedatabase.app/', None)
    cred = credentials.Certificate(access_info)
    firebase_admin.initialize_app(cred, {'storageBucket': 'cloudproject-5451f.appspot.com'})                              

    # Start ngrok
    port = 8053  # Use a different port
    public_url = ngrok.connect(port)
    print('Public URL:', public_url)

    # Run the Dash app
    app.run_server(host='0.0.0.0', port=port)
