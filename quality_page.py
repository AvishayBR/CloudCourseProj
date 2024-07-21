from dash import html, dcc

def quality_page(current_data):
    return html.Div([
        html.H1("Students Quality"),
        html.P("Select documents to filter the data:"),
        dcc.Dropdown(
            id='document-dropdown',
            options=[{'label': doc, 'value': doc} for doc in current_data['Document'].unique() if
                     not doc is None and not doc == ""],
            multi=True
        ),
        html.Button("Generate", id='generate-quality-button', n_clicks=0, className="button-generate"),
        html.Div(id='quality-data-output')
    ], className="analysis-page")
