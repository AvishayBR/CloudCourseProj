import pandas as pd
import plotly.express as px
from dash import Dash, dcc, html, Input, Output, State
import dash_bootstrap_components as dbc
from pyngrok import ngrok
import requests
import base64
import io
import datetime
import plotly.graph_objects as go

def home_page():
  return html.Div([
            html.H1("Home Page"),
            html.P("Welcome to the OnShape Analysis Tool."),
            html.P("This application is designed to help managers of OnShape crews analyze and monitor the work of their team."),
            html.P("By processing log files in JSON format from the OnShape application, this tool provides detailed statistics and insights into team performance, project progress, and collaboration efficiency."),
            html.P("Navigate to the Dashboard to see detailed visualizations and analysis."),
            html.Div(
                [
                    html.Img(src="https://cdn.sanity.io/images/tlr8oxjg/production/22c3b048689e6b8cd048157c7eb3c01cce769a41-1456x816.png", className="image-3d"),
                    html.Img(src="https://www.netscribes.com/wp-content/uploads/2023/01/Innovation-strategies.jpg", className="image-3d"),
                    html.Img(src="https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSfxTS5KrMzEwuG9QqZlNrJYB7Gfp7NdJAR4g&s", className="image-3d"),
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
            html.Div(id='output-data-upload')
        ], className = "setup-page")

def additional_page_1():
  print([doc for doc in current_data['Document'].unique()])
  return html.Div([
      html.H1("Additional Page 1"),
      html.P("Select documents to filter the data:"),
      dcc.Dropdown(
          id='document-dropdown',
          options=[{'label': doc, 'value': doc} for doc in current_data['Document'].unique() if not doc is None and not doc == ""],
          multi=True
      ),
      html.Button("Generate", id='generate-button', n_clicks=0),
      html.Div(id='filtered-data-output')
  ])


def additional_page_2():
    return html.Div([
        html.H1("Additional Page 2"),
        html.P("This is the additional page 2.")
    ])


# Initialize the Dash app
app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
current_data = pd.DataFrame()
# Define the sidebar
sidebar = html.Div(
    [
        html.Div(
            [
                html.Img(src="https://play-lh.googleusercontent.com/yAS9WJJnjlCx77RxIvJSssrixhCdUxnBlM3CuPnQpl8QI3Ez19KreBL4xREc1gtmK_Y", style={"height": "65px", "margin-right": "10px"}),  # Adjust the URL and style as needed
                html.H2("OnShape Analysis", className="display-10", style={"color": "white", "display": "inline-block", "vertical-align": "middle"})
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
        return html.Div([
            html.H1("About Page"),
            html.P("This is the about page.")
        ])
    elif pathname == "/additional-page-1":
      return additional_page_1()
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
    global current_data
    if content is not None:
        content_type, content_string = content.split(',')
        decoded = base64.b64decode(content_string)
        try:
            if 'json' in filename:
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
        except Exception as e:
            print(e)
            return html.Div([
                'There was an error processing this file.'
            ]), ''
    return html.Div(), ''

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
            dbc.NavLink("Additional Page 1", href="/additional-page-1", active="exact", className="nav-link"),
            dbc.NavLink("Additional Page 2", href="/additional-page-2", active="exact", className="nav-link"),
            dbc.NavLink("About", href="/about", active="exact", className="nav-link")
        ])
    else:
        nav_links.extend([
          dbc.NavLink("About", href="/about", active="exact", className="nav-link")
        ])
    return nav_links

# Callback to handle the Generate button click and display the graph
@app.callback(
    Output('filtered-data-output', 'children'),
    [Input('generate-button', 'n_clicks')],
    [State('document-dropdown', 'value')]
)
def generate_graph(n_clicks, selected_documents):
    if n_clicks > 0 and selected_documents:
        filtered_data = current_data[current_data['Document'].isin(selected_documents)]
        users = [User for User in current_data['User'].unique()]
        if not filtered_data.empty:
            fig = px.bar(filtered_data, x='Document', y='Value')  # Adjust 'Value' with the appropriate column
            return dcc.Graph(figure=fig)
    return html.Div("No data selected or no data available for the selected documents.")



# Get your ngrok authtoken from https://dashboard.ngrok.com/get-started/your-authtoken
NGROK_AUTH_TOKEN = '2j0ipKmlgFqppERAFqNinYRb1FH_5cmC5sMfw4DX9PdqrrDQ1'
ngrok.set_auth_token(NGROK_AUTH_TOKEN)

# Run the app with ngrok
if __name__ == '__main__':
    # Start ngrok
    port = 8053  # Use a different port
    public_url = ngrok.connect(port)
    print('Public URL:', public_url)  
    

    # Run the Dash app
    app.run_server(host='0.0.0.0', port=port)