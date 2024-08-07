import base64
import io
import datetime
import json
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import dash
from dash import dcc, html, Input, Output, State
import dash_bootstrap_components as dbc
from firebase_utils import upload_to_firebase, get_files_from_firebase, download_from_firebase, \
    fetch_patterns_from_firebase
from indexing_utils import search_engine
import data_cache
import graph_utils
import nltk
from nltk.chat.util import Chat, reflections

# Initialize NLTK components
nltk.download('punkt')
nltk.download('wordnet')

# Function to register all Dash callbacks
def register_callbacks(app, FBconn):
    # Get patterns from Database
    patterns = fetch_patterns_from_firebase('patterns.txt')

    # Create the Chatbot
    chatbot = Chat(patterns, reflections)

    # Callback to update the conversation based on user input
    @app.callback(
        [Output('conversation-container', 'children'), Output('conversation-state', 'children'),
         Output('user-input', 'value')],
        [Input('submit-button', 'n_clicks')],
        [State('user-input', 'value'), State('conversation-state', 'children')]
    )
    def update_conversation(n_clicks, user_message, conversation_state):
        if conversation_state is None:
            # Initial greeting from the chatbot
            conversation_state = [html.Div("Chatbot: Hello! How can I assist you today?", style={"color": "blue"})]
            return conversation_state, conversation_state, ''

        if n_clicks > 0 and user_message:
            # Simulate chatbot response (replace with actual chatbot logic)
            chatbot_response = chatbot.respond(user_message)

            if (chatbot_response == None):
                chatbot_response = 'I am not quite sure i understand that, feel free to ask me anything else :)'

            # Check if the user want to clear the chat
            if (user_message == 'clear'):
                conversation_state = []
                conversation_state.append(html.Div("Chat cleared...", style={"color": "blue"}))
                conversation_state.append(
                    html.Div("Chatbot: Hello! How can I assist you today?", style={"color": "blue"}))
            else:
                # Update conversation state
                conversation_state.append(html.Div(f"You: {user_message}"))
                conversation_state.append(html.Div(f"Chatbot: {chatbot_response}", style={"color": "blue"}))

            return conversation_state, conversation_state, ''  # Clear the input field

        return dash.no_update, dash.no_update, dash.no_update

    # Callback to toggle the state of the submit button based on the user input
    @app.callback(
        Output('submit-button', 'disabled'),
        Input('user-input', 'value')
    )
    def toggle_button_state(user_message):
        # Disable the button if the input field is empty
        if user_message:
            return False
        return True

    # Callback to update the glossary index based on user input
    @app.callback(
        [Output('output-container', 'children'),
         Output('index-state-table', 'children')],
        Input('submit-button', 'n_clicks'),
        State('text-input', 'value')
    )
    def update_glossary_index(n_clicks, value):
        # Define the URL of the glossary
        glossary_url = 'https://cad.onshape.com/help/Content/Glossary/glossary.htm'
        if n_clicks > 0:
            if not value: # Check if the input is empty
                return 'Cannot index an empty input', ''
            else: # Search the glossary index for the input
                result = search_engine(glossary_url, value)
                if not result:
                    return f'Cannot find any index related to {value}', ''

                # Create a table to display the search results
                keys = list(result.keys())
                values = list(result.values())

                table = go.Figure(data=[go.Table(
                    header=dict(values=['term', 'frequency'],
                                fill_color='paleturquoise',
                                align='left'),
                    cells=dict(values=[keys, values],
                               fill_color='lavender',
                               align='left'))
                ])
                return '', html.Div([
                    html.H5("The results"),
                    dcc.Graph(
                        id='table-index',
                        figure=table
                    )
                ])
        return '', ''

    # Callback to update the sidebar dynamically based on the file upload state
    @app.callback(
        Output('document-dropdown-analysis', 'value'),
        [Input('select-all-button', 'n_clicks'),
         Input('clear-all-button', 'n_clicks')],
        [State('document-dropdown-analysis', 'options')]
    )
    def update_dropdown(select_all_clicks, clear_all_clicks, options):
        ctx = dash.callback_context

        if not ctx.triggered:
            return []

        # Get the ID of the button that triggered the callback
        button_id = ctx.triggered[0]['prop_id'].split('.')[0]

        if button_id == 'select-all-button':
            return [option['value'] for option in options]
        elif button_id == 'clear-all-button':
            return []

        return []

    # Callback to update the dropdown based on the search button click
    @app.callback(
        Output('user-dropdown', 'value'),
        [Input('user-select-all-button', 'n_clicks'),
         Input('user-clear-all-button', 'n_clicks')],
        [State('user-dropdown', 'options')]
    )
    def update_dropdown2(select_all_clicks, clear_all_clicks, options):
        ctx = dash.callback_context

        if not ctx.triggered:
            return []
        # Get the ID of the button that triggered the callback
        button_id = ctx.triggered[0]['prop_id'].split('.')[0]

        if button_id == 'user-select-all-button':
            return [option['value'] for option in options]
        elif button_id == 'user-clear-all-button':
            return []

        return []

    # Callback to update the dropdown based on the search button click
    @app.callback(
        Output('document-dropdown', 'value'),
        [Input('select-all-button', 'n_clicks'),
         Input('clear-all-button', 'n_clicks')],
        [State('document-dropdown', 'options')]
    )
    def update_dropdown(select_all_clicks, clear_all_clicks, options):
        ctx = dash.callback_context

        if not ctx.triggered:
            return []
        # Get the ID of the button that triggered the callback
        button_id = ctx.triggered[0]['prop_id'].split('.')[0]

        if button_id == 'select-all-button':
            return [option['value'] for option in options]
        elif button_id == 'clear-all-button':
            return []

        return []

    # Callback to update the dropdown based on the search button click
    @app.callback(
        [Output('output-data-upload', 'children'),
         Output('upload-state', 'children')],
        [Input('upload-data', 'contents')],
        [State('upload-data', 'filename'),
         State('upload-data', 'last_modified')]
    )
    def update_output(content, filename, date):
        if content is not None: # Check if a file was uploaded
            content_type, content_string = content.split(',') # Split the content
            decoded = base64.b64decode(content_string) # Decode the content
            try:
                if '.json' in filename:
                    # Assume that the user uploaded a JSON file
                    data = pd.read_json(io.StringIO(decoded.decode('utf-8')))
                    data['Time'] = pd.to_datetime(data['Time'])  # Convert 'Time' column to datetime
                    data_cache.update_current_data(data) # Update the current data
                    table = go.Figure(data=[go.Table(
                        header=dict(values=list(data.columns),
                                    fill_color='paleturquoise',
                                    align='left'),
                        cells=dict(values=[data[col] for col in data.columns],
                                   fill_color='lavender',
                                   align='left'))
                    ])
                    return html.Div([
                        html.H5(filename),
                        html.H6(datetime.datetime.fromtimestamp(date)),
                        dcc.Graph(
                            id='table-graph',
                            figure=table
                        )
                    ]), 'uploaded'
                else:
                    return html.Div([
                        'Must upload a file with format .json only'
                    ]), ''
            except Exception as e:
                print(e)
                return html.Div([
                    'There was an error processing this file.'
                ]), ''
        return html.Div(), ''

    # Callback to update the sidebar dynamically based on the file upload state
    @app.callback(
        Output('save-button', 'style'),
        [Input('upload-state', 'children')]
    )
    def show_save_button(upload_state):
        if upload_state == 'uploaded':
            return {"display": "block", "margin": "auto", "margin-top": "20px"}
        return {"display": "none"}

    # Callback to update the dropdown based on the search button click
    @app.callback(
        Output('file-dropdown', 'options'),
        Output('file-dropdown', 'style'),
        Input('search-button', 'n_clicks')
    )
    def update_dropdown(n_clicks):
        if n_clicks > 0:
            files = get_files_from_firebase()
            files = [file for file in files if file != 'patterns.txt']
            options = [{'label': file, 'value': file} for file in files]
            return options, {"margin": "auto", "margin-top": "20px", "display": "block"}
        return [], {"display": "none"}

    # Callback to update the dropdown based on the search button click
    @app.callback(
        Output('save-state', 'children'),
        [Input('save-button', 'n_clicks')],
        [State('upload-data', 'contents'),
         State('upload-data', 'filename')]
    )
    def save_to_firebase(n_clicks, content, filename):
        if n_clicks > 0 and content is not None:
            content_type, content_string = content.split(',')
            decoded = base64.b64decode(content_string)
            try:
                if '.json' in filename:
                    new_data = json.loads(decoded.decode('utf-8'))
                    # Fetch existing data from Firebase
                    existing_data = FBconn.get('/shablool/', None)
                    # Handle case where existing_data is None
                    if existing_data is None:
                        FBconn.post('/shablool/', new_data)
                        data_url = upload_to_firebase(filename, decoded)
                    # Check if new data is already in the database
                    elif new_data not in existing_data.values():
                        # Post to Firebase
                        FBconn.post('/shablool/', new_data)
                        data_url = upload_to_firebase(filename, decoded)
                    else:
                        return 'Data already exists in the database'
                    return 'Data saved successfully'
            except Exception as e:
                print(e)
                return 'Error saving data'
        return ''

    # Callback to update the dropdown based on the search button click
    @app.callback(
        [Output('output-search-state', 'children'),
         Output('output-analysis', 'children')],
        Input('file-dropdown', 'value')
    )
    def display_file(filename):
        if filename:
            content = download_from_firebase(filename)
            data = pd.read_json(io.StringIO(content))
            data['Time'] = pd.to_datetime(data['Time'])  # Convert 'Time' column to datetime
            data_cache.update_current_data(data)
            table = go.Figure(data=[go.Table(
                header=dict(values=list(data.columns),
                            fill_color='paleturquoise',
                            align='left'),
                cells=dict(values=[data[col].tolist() for col in data.columns],
                           fill_color='lavender',
                           align='left'))
            ])
            return dcc.Graph(figure=table), 'uploaded'
        return html.Div(), ''

    # Callback to update the sidebar dynamically based on the file upload state
    @app.callback(
        Output('sidebar-nav', 'children'),
        [Input('upload-state', 'children'),
         Input('output-analysis', 'children'),
         Input('url', 'pathname')]
    )
    def update_sidebar(upload_state, output_analysis, pathname):
        nav_links = [ # Define the default links
            dbc.NavLink("Home", href="/", active="exact", className="nav-link"),
            dbc.NavLink("Setup", href="/setup", active="exact", className="nav-link"),

        ]
        if (upload_state == 'uploaded' or output_analysis == 'uploaded'):   # Check if a file was uploaded
            nav_links.extend([ # Add the following links to the sidebar
                dbc.NavLink("Analysis & Statistics", href="/analysis", active="exact", className="nav-link"),
                dbc.NavLink("Students Quality Board", href="/quality", active="exact", className="nav-link"),
            ])
        nav_links.extend([ # Add the following links to the sidebar
            dbc.NavLink("Glossary Index", href="/index", active="exact" if pathname == "/index" else False,
                        className="nav-link"),
            dbc.NavLink("Chatbot", href="/chat", active="exact" if pathname == "/chat" else False,
                        className="nav-link"),
            dbc.NavLink("About", href="/about", active="exact" if pathname == "/about" else False, className="nav-link")
        ])

        return nav_links

    # Callback to the graphs based on the user input
    @app.callback(
        Output('filtered-data-output', 'children'),
        [Input('generate-button', 'n_clicks')],
        [State('document-dropdown-analysis', 'value'),
         State('user-dropdown', 'value'),
         State('date-picker-range', 'start_date'),
         State('date-picker-range', 'end_date')]
    )
    def generate_graph(n_clicks, selected_documents, selected_users, start_date, end_date):
        if n_clicks > 0:
            current_data = data_cache.get_current_data()

            if selected_documents: # Check if documents are selected
                current_data = current_data[current_data['Document'].isin(selected_documents)]

            if selected_users: # Check if users are selected
                current_data = current_data[current_data['User'].isin(selected_users)]

            if start_date and end_date: # Check if a date range is selected
                current_data['Time'] = pd.to_datetime(current_data['Time'])
                current_data = current_data[(current_data['Time'] >= start_date) & (current_data['Time'] <= end_date)]

            if not current_data.empty:
                # Group data by 'User' and 'Document', then calculate session durations
                session_data = pd.DataFrame()
                for (user, document), group in current_data.groupby(['User', 'Document']):
                    user_document_sessions = graph_utils.session_durations(group).copy()
                    user_document_sessions.loc[:, 'Document'] = document
                    session_data = pd.concat([session_data, user_document_sessions])

                # Summarize the time spent by each user for each document
                user_document_time_spent = session_data.groupby(['User', 'Document'])[
                    'Session_Duration'].sum().reset_index()
                user_document_time_spent['Session_Duration_hours'] = user_document_time_spent[
                                                                         'Session_Duration'].dt.total_seconds() / 3600

                # Create the bar chart for session time spent by each user on each document
                time_spent_fig = px.bar(user_document_time_spent, x='User', y='Session_Duration_hours',
                                        color='Document',
                                        labels={'Session_Duration_hours': 'Session Duration (hours)'},
                                        title='Session Duration by Each User on Each Document',
                                        barmode='group')

                # Generate other required plots
                total_interactions_fig = go.Figure(go.Indicator(
                    mode="number",
                    value=graph_utils.total_interactions(current_data),
                    title={"text": "Total Interactions"}
                ))
                # Generate the rest of the plots
                interactions_by_type_counts = graph_utils.count_interactions_by_type(current_data)
                interactions_by_type_fig = px.bar(interactions_by_type_counts, x=interactions_by_type_counts.index,
                                                  y=interactions_by_type_counts.values,
                                                  labels={'index': 'Interaction Type', 'y': 'Count'},
                                                  title='Interactions by Type')

                interactions_over_time_counts = graph_utils.interactions_over_time(current_data)
                interactions_over_time_fig = px.line(interactions_over_time_counts,
                                                     x=interactions_over_time_counts.index,
                                                     y=interactions_over_time_counts.values,
                                                     labels={'index': 'Time', 'y': 'Count'},
                                                     title='Interactions Over Time')

                interactions_by_user_counts = graph_utils.interactions_by_user(current_data)
                interactions_by_user_fig = px.bar(interactions_by_user_counts, x=interactions_by_user_counts.index,
                                                  y=interactions_by_user_counts.values,
                                                  labels={'index': 'User', 'y': 'Count'}, title='Interactions by User')

                interactions_by_time_of_day_counts = graph_utils.interactions_by_time_of_day(current_data)
                interactions_by_time_of_day_fig = px.bar(interactions_by_time_of_day_counts,
                                                         x=interactions_by_time_of_day_counts.index,
                                                         y=interactions_by_time_of_day_counts.values,
                                                         labels={'index': 'Hour of Day', 'y': 'Count'},
                                                         title='Interactions by Time of Day')

                return html.Div([
                    dcc.Graph(figure=total_interactions_fig),
                    dcc.Graph(figure=interactions_by_type_fig),
                    dcc.Graph(figure=interactions_over_time_fig),
                    dcc.Graph(figure=interactions_by_user_fig),
                    dcc.Graph(figure=interactions_by_time_of_day_fig),
                    dcc.Graph(figure=time_spent_fig)
                ])
        return html.Div("No data selected or no data available for the selected documents.")

    # Callback to update the quality graph based on the user input
    @app.callback(
        Output('quality-data-output', 'children'),
        [Input('generate-quality-button', 'n_clicks')],
        [State('document-dropdown', 'value')]
    )
    def generate_quality_graph(n_clicks, selected_documents):
        if n_clicks > 0 and selected_documents:
            current_data = data_cache.get_current_data()
            filtered_data = current_data[current_data['Document'].isin(selected_documents)]
            deleting_percentage, average = graph_utils.get_users_adding_interations(filtered_data)
            df = pd.DataFrame(list(deleting_percentage.items()), columns=['Student', 'Quality Percentage'])

            # Sort the DataFrame by 'Value' in descending order and get the top 3
            top_3 = df.nlargest(3, 'Quality Percentage')

            # SVG for the first place
            first_place_svg = '''
            <svg class="podium__number" viewBox="0 0 27.476 75.03" xmlns="http://www.w3.org/2000/svg">
                <g transform="matrix(1, 0, 0, 1, 214.957736, -43.117417)">
                    <path class="st8" d="M -198.928 43.419 C -200.528 47.919 -203.528 51.819 -207.828 55.219 C -210.528 57.319 -213.028 58.819 -215.428 60.019 L -215.428 72.819 C -210.328 70.619 -205.628 67.819 -201.628 64.119 L -201.628 117.219 L -187.528 117.219 L -187.528 43.419 L -198.928 43.419 L -198.928 43.419 Z" style="fill: #000;"/>
                </g>
            </svg>
            '''

            # Create a podium display
            podium = html.Div(className="container podium", children=[
                html.Div(className="podium__item", children=[
                    html.P(className="podium__city", children=top_3.iloc[1]['Student'] if len(top_3) > 1 else ""),
                    html.Div(className="podium__rank second", children="2")
                ]),
                html.Div(className="podium__item", children=[
                    html.P(className="podium__city", children=top_3.iloc[0]['Student'] if len(top_3) > 0 else ""),
                    html.Div(className="podium__rank first", children="1")
                ]),
                html.Div(className="podium__item", children=[
                    html.P(className="podium__city", children=top_3.iloc[2]['Student'] if len(top_3) > 2 else ""),
                    html.Div(className="podium__rank third", children="3")
                ])
            ])
            df['Color'] = df['Quality Percentage'].apply(
                lambda x: 'Below Threshold' if x < average else (
                    'Above Threshold' if x not in top_3["Quality Percentage"].values else (
                        '1st Place Performer' if x == top_3.iloc[0]['Quality Percentage'] else (
                            '2nd Place Performer' if x == top_3.iloc[1]['Quality Percentage'] else
                            '3rd Place Performer'
                        )
                    )))
            df_sorted = df.sort_values(by='Quality Percentage', ascending=False)
            fig = px.bar(df_sorted, x='Student', y='Quality Percentage', color='Color', title='Students Quality Bar',
                         color_discrete_map={
                             'Below Threshold': 'red',
                             'Above Threshold': 'blue',
                             '1st Place Performer': 'gold',
                             '2nd Place Performer': 'silver',
                             '3rd Place Performer': 'chocolate'
                         },labels={'Quality Percentage': 'Student Rate'})

            return html.Div([
                html.H3("Top Performers Podium", className="podium-heading"),
                podium,
                dcc.Graph(figure=fig)
            ])

    return html.Div()
