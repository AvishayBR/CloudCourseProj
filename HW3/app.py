import pandas as pd
import sys
from dash import Dash, dcc, html, Input, Output, State
import dash_bootstrap_components as dbc
from firebase import firebase
from pyngrok import ngrok
import firebase_admin
from firebase_admin import credentials, storage
from home_page import home_page
from setup_page import setup_page
from analysis_page import analysis_page
from glossary_index_page import page_index
from about_page import about_page
from quality_page import quality_page
from firebase_utils import upload_to_firebase, get_files_from_firebase, download_from_firebase, fetch_patterns_from_firebase
from callbacks import register_callbacks
from chat_page import chat_page
import data_cache
import os
from dotenv import load_dotenv

load_dotenv()
# Initialize the Dash app
app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

app.title = "Cloud Course Project"
current_data = data_cache.get_current_data()


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
                dbc.NavLink("Chatbot", href="/chat", active="exact", className="nav-link"),
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
        return analysis_page(data_cache.get_current_data())
    elif pathname == "/index":
        return page_index()
    elif pathname == "/quality":
        return quality_page(data_cache.get_current_data())
    elif pathname == "/chat":
        return chat_page()
    else:
        return html.Div([
            html.H1("404: Not found"),
            html.P("The requested page was not found.")
        ])


# Get your ngrok authtoken from https://dashboard.ngrok.com/get-started/your-authtoken
NGROK_AUTH_TOKEN = os.getenv('NGROK_AUTH_TOKEN')
ngrok.set_auth_token(NGROK_AUTH_TOKEN)

# Run the app with ngrok
if __name__ == '__main__':
    # Connect to Firebase
    access_info = {
        "type": os.getenv('FIREBASE_TYPE'),
        "project_id": os.getenv('FIREBASE_PROJECT_ID'),
        "private_key_id": os.getenv('FIREBASE_PRIVATE_KEY_ID'),
        "private_key": os.getenv('FIREBASE_PRIVATE_KEY'),
        "client_email": os.getenv('FIREBASE_CLIENT_EMAIL'),
        "client_id": os.getenv('FIREBASE_CLIENT_ID'),
        "auth_uri": os.getenv('FIREBASE_AUTH_URI'),
        "token_uri": os.getenv('FIREBASE_TOKEN_URI'),
        "auth_provider_x509_cert_url": os.getenv('FIREBASE_AUTH_PROVIDER_CERT_URL'),
        "client_x509_cert_url": os.getenv('FIREBASE_CLIENT_CERT_URL'),
        "universe_domain": os.getenv('FIREBASE_UNIVERSE_DOMAIN'),
    }
    cred = credentials.Certificate(access_info)
    firebase_admin.initialize_app(cred, {'storageBucket': 'cloudcourseproject-d1895.appspot.com'})
    FBconn = firebase.FirebaseApplication(
        os.getenv('FIREBASE_DATABASE_URL'), None)
    register_callbacks(app, FBconn)

    # Start ngrok
    port = 8053  # Use a different port
    public_url = ngrok.connect(port)
    print('Public URL:', public_url)

    # Run the Dash app
    app.run_server(host='0.0.0.0', port=port)
