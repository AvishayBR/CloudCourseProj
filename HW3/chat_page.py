from dash import html, dcc

def chat_page():
    return html.Div([
        html.H1("OnShape Chatbot Assistance"),
        html.H4("Interact with the chatbot by typing your message below."),
        
        # Container for the chatbot conversation
        html.Div(id='conversation-container', children=[], style={
            "maxHeight": "400px", "overflowY": "auto", "border": "1px solid #ccc",
            "padding": "10px", "margin": "20px 0"
        }),
        
        # Input field and submit button for user messages
        dcc.Input(id='user-input', type='text', placeholder='Type your message...', style={"width": "80%", "marginRight": "10px"}),
        html.Button('Send', id='submit-button', n_clicks=0, style={"margin": "10px"}, className="setup-button", disabled=True),
        html.Div(html.P("Type 'clear' in order to clear the chat window", style={"color": "grey"})),
        
        # Hidden div for storing conversation state
        html.Div(id='conversation-state', style={"display": "none"})
    ], className="setup-page")
