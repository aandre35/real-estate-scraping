import pandas as pd
import plotly.express as px  # (version 4.7.0 or higher)
import plotly.graph_objects as go
from dash import Dash, html, dcc, Output, Input
from paru_vendu_data import get_data_by_cp

# Données issues du dataset
#df = pd.read_csv("data/df.csv")
df = get_data_by_cp("75000")

# Différents secteurs disponibles
secteurs = df['code postal'].unique()


app = Dash(__name__)
server = app.server

app.layout = html.Div([

    html.H1("Scraping des prix de l'immobilier", style={
        'text-align': 'center',
        'font-family': 'Roboto'
    }),

    # Prix des logements en fonction de la surface
    dcc.Dropdown(id="surface_max",
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
    
    dcc.Graph(id='graph_surface_price', figure={}),
    
    
    # Prix au m2 en fonction du nombre de pieces
    html.Br(),
    html.Div(id='output_container_2', children=[]),
    
    dcc.Dropdown(id="secteur",
                options=[{"label": sec, "value": sec} for sec in secteurs],
                multi=False,
                value=secteurs[0],
                style={'width': "40%"}
                ),
    dcc.Graph(id='graph_price_piece', figure={})

])

# ------------------------------------------------------------------------------
# Connect the Plotly graphs with Dash Components
@app.callback(
    [
        Output(component_id='output_container', component_property='children'),
        Output(component_id='graph_surface_price', component_property='figure')
    ],
    [
        Input(component_id='surface_max', component_property='value')
    ]
)
def update_graph_surface_price(option_slctd):
    
    dff = df[df['surface'] < option_slctd ] 
    container = "The max surface chosen by user is: {}".format(option_slctd)


    # Plotly Express
    fig = px.scatter(dff, x="surface", y="price", color="code postal")


    return container, fig


@app.callback(
    [
        Output(component_id='output_container_2', component_property='children'),
        Output(component_id='graph_price_piece', component_property='figure')
    ],
    [
        Input(component_id='secteur', component_property='value')
    ]
)
def update_graph_price_piece(option_slctd):
    print(option_slctd)
    df_price_surface = df[df['code postal'] == option_slctd].groupby("pieces").mean().reset_index()
    print(df_price_surface)
    
    container = "Le secteur choisi est : {}".format(option_slctd)
    
    # Plotly Express
    fig = px.bar(df_price_surface, x="pieces", y="prix au m2")

    return container, fig


# ------------------------------------------------------------------------------
if __name__ == '__main__':
    app.run_server(debug=True, host='127.0.0.1')