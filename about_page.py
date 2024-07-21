from dash import html

def about_page():
    return html.Div([
        html.H1("About Page"),
        html.P("Welcome to the About page of our application."),
        html.P("This application is designed to analyze and monitor the work of OnShape teams."),
        html.P(
            "It processes log files in JSON format to provide insights into team performance, project progress, and collaboration efficiency."),
        html.P("Navigate through the different pages to explore visualizations and detailed statistics.")
    ], style={'padding': '20px'}, className="setup-page")
