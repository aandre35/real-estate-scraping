import pandas as pd
import plotly.express as px  # (version 4.7.0 or higher)
import plotly.graph_objects as go
from dash import Dash, html, dcc, Output, Input

df = pd.read_csv("data/df.csv")

app = Dash(__name__)
server = app.server

app.layout = html.Div([

    html.H1("Web Application Dashboards with Dash", style={'text-align': 'center'}),

    dcc.Dropdown(id="slct_year",
                 options=[
                     {"label": "50 m2", "value": 50},
                     {"label": "100 m2", "value": 100},
                     {"label": "150 m2", "value": 150},
                     {"label": "200 m2", "value": 200},
                     {"label": "max", "value": 1000000}],
                 multi=False,
                 value=50,
                 style={'width': "40%"}
                 ),

    html.Div(id='output_container', children=[]),
    html.Br(),

    dcc.Graph(id='grah_surface_price', figure={}),
    

])

# ------------------------------------------------------------------------------
# Connect the Plotly graphs with Dash Components
@app.callback(
    [Output(component_id='output_container', component_property='children'),
     Output(component_id='grah_surface_price', component_property='figure')],
    [Input(component_id='slct_year', component_property='value')]
)
def update_graph(option_slctd):
    
    dff = df[df['surface'] < option_slctd ] 
    container = "The max surface chosen by user is: {}".format(option_slctd)


    # Plotly Express
    fig = px.scatter(dff, x="surface", y="price", color="code postal")


    return container, fig

# ------------------------------------------------------------------------------
if __name__ == '__main__':
    app.run_server(debug=True, host='127.0.0.1')