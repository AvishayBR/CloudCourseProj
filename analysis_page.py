from dash import html, dcc
import pandas as pd

def analysis_page(current_data):
    # Ensure 'Time' column is in datetime format
    current_data['Time'] = pd.to_datetime(current_data['Time'], errors='coerce')

    start_date = current_data['Time'].min().date() if not current_data['Time'].isnull().all() else None
    end_date = current_data['Time'].max().date() if not current_data['Time'].isnull().all() else None

    return html.Div([
        html.H1("Analysis & Statistics"),
        html.P("Select documents to filter the data:"),
        dcc.Dropdown(
            id='document-dropdown',
            options=[{'label': doc, 'value': doc} for doc in current_data['Document'].unique() if doc],
            multi=True
        ),
        html.P("Select users to filter the data:"),
        dcc.Dropdown(
            id='user-dropdown',
            options=[{'label': user, 'value': user} for user in current_data['User'].unique() if user],
            multi=True
        ),
        html.P("Select date range to filter the data:"),
        dcc.DatePickerRange(
            id='date-picker-range',
            start_date=start_date,
            end_date=end_date,
            display_format='YYYY-MM-DD'
        ),
        html.Button("Generate", id='generate-button', n_clicks=0, className="button-generate"),
        html.Div(id='filtered-data-output')
    ], className="analysis-page")
