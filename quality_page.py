from dash import html, dcc

def quality_page(current_data):
    return html.Div([
        html.H1("Students Quality"),
        html.P("Select documents to filter the data:"),
        html.Div([
            html.Button("Select All", id='select-all-button', n_clicks=0, className="button-select-all"),
            html.Button("Clear All", id='clear-all-button', n_clicks=0, className="button-clear-all"),
            dcc.Dropdown(
                id='document-dropdown',
                options=[{'label': doc, 'value': doc} for doc in current_data['Document'].unique() if
                         not doc is None and not doc == ""],
                multi=True,
                className="dropdown"
            ),
        ], className="button-dropdown-container"),
        html.Button("Generate", id='generate-quality-button', n_clicks=0, className="button-generate"),
        html.Div(id='quality-data-output')
    ], className="analysis-page")