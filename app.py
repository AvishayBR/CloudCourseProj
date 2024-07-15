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
import json




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
    sessions = sessions[(sessions['Description'].str.contains('Open document')) & (sessions['User'] == sessions['Next_User'])]
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


def setup_page():
    return html.Div([
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
        html.Button("Save", id="save-button", n_clicks=0, style={"display": "none", "margin": "auto", "margin-top": "20px"}, className = "save-button"),
        html.Div(id='save-state', style={"display": "none", "margin": "auto", "margin-top": "20px"}),
    ], className="setup-page")


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
        html.Button("Generate", id='generate-button', n_clicks=0, className ="button-generate"),
        html.Div(id='filtered-data-output')
    ], className="analysis-page")


def additional_page_2():
    return html.Div([
        html.H1("Additional Page 2"),
        html.P("This is the additional page 2.")
    ])


def about_page():
    return html.Div([
        html.H1("About Page"),
        html.P("Welcome to the About page of our application."),
        html.P("This application is designed to analyze and monitor the work of OnShape teams."),
        html.P("It processes log files in JSON format to provide insights into team performance, project progress, and collaboration efficiency."),
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
    else:
        return html.Div([
            html.H1("404: Not found"),
            html.P("The requested page was not found.")
        ])


# Callback to handle file upload and convert JSON to DataFrame
@app.callback(
    [Output('output-data-upload', 'children'),
     Output('upload-state', 'children')],
    [Input('upload-data', 'contents')],
    [State('upload-data', 'filename'),
     State('upload-data', 'last_modified')]
)

def update_output(content, filename, date):
    if content is not None:
        content_type, content_string = content.split(',')
        decoded = base64.b64decode(content_string)
        try:
            if 'json' in filename:
                # Assume that the user uploaded a JSON file
                data = pd.read_json(io.StringIO(decoded.decode('utf-8')))
                # result = FBconn.post('/shablool/', data.to_dict())
                table = go.Figure(data=[go.Table(
                    header = dict(values=list(data.columns),
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
    Output('save-state', 'children'),
    [Input('save-button', 'n_clicks')],
    [State('upload-data', 'contents'),
     State('upload-data', 'filename')]
)
def save_to_firebase(n_clicks, content, filename):
    global FBconn
    if n_clicks > 0 and content is not None:
        content_type, content_string = content.split(',')
        decoded = base64.b64decode(content_string)
        try:
            if 'json' in filename:
                data = json.loads(decoded.decode('utf-8'))
                # Post to Firebase
                FBconn.post('/shablool/', data)
                return 'Data saved successfully'
        except Exception as e:
            print(e)
            return 'Error saving data'
    return ''

# Callback to update the sidebar dynamically based on the file upload state
@app.callback(
    Output('sidebar-nav', 'children'),
    [Input('upload-state', 'children')]
)
def update_sidebar(upload_state):
    nav_links = [
        dbc.NavLink("Home", href="/", active="exact", className="nav-link"),
        dbc.NavLink("Setup", href="/setup", active="exact", className="nav-link"),

    ]
    if upload_state == 'uploaded':
        nav_links.extend([
            dbc.NavLink("Analysis & Statistics", href="/analysis", active="exact", className="nav-link"),
            dbc.NavLink("Additional Page 2", href="/additional-page-2", active="exact", className="nav-link"),
            dbc.NavLink("About", href="/about", active="exact", className="nav-link")
        ])
    else:
        nav_links.extend([
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
            interactions_by_type_fig = px.bar(interactions_by_type_counts, x=interactions_by_type_counts.index, y=interactions_by_type_counts.values,
                                              labels={'index': 'Interaction Type', 'y': 'Count'}, title='Interactions by Type')

            interactions_over_time_counts = interactions_over_time(filtered_data)
            interactions_over_time_fig = px.line(interactions_over_time_counts, x=interactions_over_time_counts.index, y=interactions_over_time_counts.values,
                                                 labels={'index': 'Time', 'y': 'Count'}, title='Interactions Over Time')

            interactions_by_user_counts = interactions_by_user(filtered_data)
            interactions_by_user_fig = px.bar(interactions_by_user_counts, x=interactions_by_user_counts.index, y=interactions_by_user_counts.values,
                                              labels={'index': 'User', 'y': 'Count'}, title='Interactions by User')


            interactions_by_time_of_day_counts = interactions_by_time_of_day(filtered_data)
            interactions_by_time_of_day_fig = px.bar(interactions_by_time_of_day_counts, x=interactions_by_time_of_day_counts.index, y=interactions_by_time_of_day_counts.values,
                                                     labels={'index': 'Hour of Day', 'y': 'Count'}, title='Interactions by Time of Day')

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

    # Start ngrok
    port = 8053  # Use a different port
    public_url = ngrok.connect(port)
    print('Public URL:', public_url)

    # Run the Dash app
    app.run_server(host='0.0.0.0', port=port)
