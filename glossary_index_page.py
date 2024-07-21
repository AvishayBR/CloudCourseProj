from dash import html, dcc

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
