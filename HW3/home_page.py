from dash import html, dcc

def home_page():
    return html.Div([
        html.H1("Home Page"),
        html.P("Welcome to the OnShape Analysis Tool."),
        html.P(
            "This application is designed to help managers of OnShape crews analyze and monitor the work of their team."),
        html.P(
            "By processing log files in JSON format from the OnShape application, this tool provides detailed statistics and insights into team performance, project progress, and collaboration efficiency."),
        html.P("Navigate to the Dashboard to see detailed visualizations and analysis."),
        html.Div(
            [
                html.Img(
                    src="https://cdn.sanity.io/images/tlr8oxjg/production/22c3b048689e6b8cd048157c7eb3c01cce769a41-1456x816.png",
                    className="image-3d"),
                html.Img(src="https://www.netscribes.com/wp-content/uploads/2023/01/Innovation-strategies.jpg",
                         className="image-3d"),
                html.Img(
                    src="https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSfxTS5KrMzEwuG9QqZlNrJYB7Gfp7NdJAR4g&s",
                    className="image-3d"),
            ],
            style={"display": "flex", "justify-content": "space-around", "margin-top": "40px"}
        )
    ], className="home-page")
