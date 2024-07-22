from dash import Dash, html

app = Dash(__name__)


def about_page():
    contributors = [
        {"name": "Avishay Bar", "image": "/assets/Avishay.jpg"},
        {"name": "Ron Bendel", "image": "/assets/Ron.jpg"},
        {"name": "Tamer Amer", "image": "/assets/Tamer.jpg"},
        {"name": "Bahaldeen Swied", "image": "/assets/Bhaa.jpg"},
        {"name": "Rabea Lahham", "image": "/assets/Rabea.jpg"}
    ]

    contributors_section = html.Div([
        html.H2("Contributors"),
        html.Div([
            html.Div([
                html.Img(src=contributor["image"], className="contributor-image"),
                html.P(contributor["name"])
            ], className="contributor") for contributor in contributors
        ], className="contributors-container")
    ])

    contact_section = html.Div([
        html.H2("Contact Us"),
        html.P("E-Mail: CloudCourse123@gmail.com"),
        html.P("Phone:+972535302166")
    ], className="contact-section")

    return html.Div([
        html.H1("About Page"),
        html.P("Welcome to the About page of our application."),
        html.P("This application is designed to analyze and monitor the work of OnShape teams."),
        html.P(
            "It processes log files in JSON format to provide insights into team performance, project progress, and collaboration efficiency."),
        html.P("Navigate through the different pages to explore visualizations and detailed statistics."),
        contributors_section,
        contact_section
    ], style={'padding': '20px'}, className="setup-page")
