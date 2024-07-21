from dash import html, dcc

def analysis_page(current_data):
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
