from dash import html, dcc

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
