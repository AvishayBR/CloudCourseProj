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
from firebase_utils import upload_to_firebase, get_files_from_firebase, download_from_firebase
from callbacks import register_callbacks
import data_cache
# Initialize the Dash app
app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
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
    else:
        return html.Div([
            html.H1("404: Not found"),
            html.P("The requested page was not found.")
        ])


# Get your ngrok authtoken from https://dashboard.ngrok.com/get-started/your-authtoken
NGROK_AUTH_TOKEN = '2j0ipKmlgFqppERAFqNinYRb1FH_5cmC5sMfw4DX9PdqrrDQ1'
ngrok.set_auth_token(NGROK_AUTH_TOKEN)

# Run the app with ngrok
if __name__ == '__main__':
    # Connect to Firebase
    access_info = {
        "type": "service_account",
        "project_id": "cloudcourseproject-d1895",
        "private_key_id": "45c14d06d6e8d9972cc313c45df2bb8772a27871",
        "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEvgIBADANBgkqhkiG9w0BAQEFAASCBKgwggSkAgEAAoIBAQC5WbT0ofhOulC1\nANZrG8aRDQrnOcdBLIDxZcLEXsV2xTecG7EruU3Qm8rcwNZyRy0enhiQ1fl9BPcX\nqNDE9Vsn8xSOnEY/7tNMIGy6bSWSZNSXNaXGnaM9mzuHzd/hpgqiMRasHW53ImEj\n6W3+H/A9C97l2xRK6PoIT90GCDyLBoGQr3QiUKPgeBG0Wz06oUsvCiV/Nw0J3hqr\nCd+JVamkShvC2oNhaL5HNlSZAvfx+MI3znKNlbqRSO6ZrBGcagzGhPxl1SICq3FS\n4bokQJzD2KgMd/IqPYpG5vEILwm0QEkHVF4LdnY6JARvz/Z9NeTN94nWoDGX0c7g\nbZR4oot3AgMBAAECggEAW5frBmDsFeuYannpe7CUJaXuV2mD/78AUUpaPzQeHJ1E\n583/dX3y6D20t/ZLgtmNgG3b8ebrjU5g1L5FvK8KxukmpXqwdHOO0zXKxS2evYM6\nUybdrxLDUnRdrLSeCCJHavMbIx7AMfs5ScfW5RffXit5kNj8ZDBRLr5YmNyFHqXV\nw0UDKYwjeDSI+CAX0cSgBo+AJLzunztLlxs6dBa/im3h94zS1XJc2gz4eBxoq19p\nAucmoYWwp5pyfLzc3QI9+2c7X39kxceIhr5krr7FyA9eX9oXhwtyIii4BDgVk5w7\nQG/ztVmu7Efl6N3m5ZJN+5fQSfEoUEMbt+9VoU5YUQKBgQDz3U0JA5i0TpQf4HD8\nMrh2yZrlW89tFqF2CruWp8kqk7nX2qVUQKqI/ok6IMW9rFVaBUFAg0nTUB+tnzf3\nt7Xeazi2BqdEsfbGg7BFjjUUHjwOzH5NKC3zU96D9GcUyUR/rT+FRKUbhBliItCj\nbsjFFr5ILpv6fTFqMuwI7exbhQKBgQDCkvghDIsXtPytSgyv5xHve+dA3ReigoyB\nUiNdrPkwLsukURCI/F9FW9KZVK1XTLRV83idjc/AYpLDriWsouWTyrpldoHzuTwC\nGypYg/7BdX6zJtWu7WP0Xp/QhrK165X3w0BOLphH1ce2MtmrJmI4EBbfRueA6AqV\noYOmsnjlywKBgQCYXz1EFZgziSmqZT2Th0mVB1EeYGhR3CMUs44Ui0/5p4YmZjqJ\nU0J7CLfLtzB23BgUgFYOLjpRq62veV2qDYK4r7wmmC+pj50G2r+oJjvqDx4tjP6Z\nzTIw6MWPI4XJCh0fvauD5KlZcQe/NsuwYodWBmjshxr0v4bBuYGb7rWRVQKBgQC8\nMyfp35YSIi9c9gj7g4dnmvL9XFzmBVweIfKvQwXsQvcaQoa52VHVZpF3Wd4oWLr9\nf/gkfOx761yGBUXPi+h/YVGVnmDn+z091ETLRTD+ssUQR/nbryZFUdlG+2KUcACo\nm6TxekQ1B2SaqOi9kOzjyTw2TwDRQKAsRwNuE6a4rQKBgFJw462fhT4yLqfmZzf3\nYkQCt7vmIXH70wYG6zHjbmmwYvj0Btz49oiGLfHM23XUr0posmj8Dv2OS1Q2G+3z\noDBMZ+/918HGmo7H/ab0GpaejnFPv88bglQ+DxdzPTUrOOl5t33WbWfkrOmyI32c\ndue2XIGabShdjg+VVs3woSth\n-----END PRIVATE KEY-----\n",
        "client_email": "firebase-adminsdk-7ziaq@cloudcourseproject-d1895.iam.gserviceaccount.com",
        "client_id": "114928397654101951903",
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://oauth2.googleapis.com/token",
        "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
        "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/firebase-adminsdk-7ziaq%40cloudcourseproject-d1895.iam.gserviceaccount.com",
        "universe_domain": "googleapis.com"
    }
    cred = credentials.Certificate(access_info)
    firebase_admin.initialize_app(cred, {'storageBucket': 'cloudcourseproject-d1895.appspot.com'})
    FBconn = firebase.FirebaseApplication(
        'https://cloudcourseproject-d1895-default-rtdb.europe-west1.firebasedatabase.app/', None)
    register_callbacks(app, FBconn)

    # Start ngrok
    port = 8053  # Use a different port
    public_url = ngrok.connect(port)
    print('Public URL:', public_url)

    # Run the Dash app
    app.run_server(host='0.0.0.0', port=port)
