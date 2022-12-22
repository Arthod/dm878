
import json
from scipy import signal
import plotly.graph_objects as go
import ipywidgets as widgets
import pandas as pd
import numpy as np
from datetime import datetime
import plotly.express as px
from dash.dependencies import Input, Output

import dash
from dash import dcc
from dash import html

import utils

import os

from civilwar_preprocessing import preprocess

# https://data.world/kieroneil/us-civil-war-1861-1865/workspace/file?filename=cwsac_battles.csv


time_old = [0, 0]
f_json = open("us-states-geojson.json")
usa_geojson = json.load(f_json)
f_json.close()

if (not os.path.exists("dataset/cwsac_battles_pp.csv")):
    preprocess()

cwsac_battles = pd.read_csv("dataset/cwsac_battles_pp.csv", encoding='utf-8')
cwsac_battles["strength"] = cwsac_battles["strength"].fillna(0)
cwsac_battles["casualties"] = cwsac_battles["casualties"].fillna(0)
cwsac_battles["start_date"] = pd.to_datetime(cwsac_battles["start_date"])
print(cwsac_battles.head())



app = dash.Dash()


mintime = 1861 + (4/12)
maxtime = 1865 + (4/12)

QUARTERS = ["January", "April", "July", "October"]

app.layout = html.Div([
    html.H1(children="American Civil War (1861-1865)",
            style={'textAlign': 'center', 'font-family': 'Roboto, sans-serif', "padding-bottom": "0px"}),
    html.Div(className='container', children=[
        html.Div(className='row', children=[
            html.Div([
                html.Div([
                    dcc.Dropdown(["result", "campaign"], "result", id="dropdownPickType"),
                ], style={'width': '10%', 'display': 'inline-block', 'vertical-align': 'top', 'margin': '1%'}),
                html.Div([
                    dcc.Graph(id="geomap"),
                    dcc.RangeSlider(
                        id='time-slider',
                        min=mintime,
                        max=maxtime,
                        step=1/12,
                        value=[mintime, maxtime],
                        marks={
                            mintime: "1861-Apr", 1861 + (7/12): "1861-Jul", 1861 + (10/12): "1861-Oct",
                            1862 + (1/12): "1862-Jan", 1862 + (4/12): "1862-Apr", 1862 + (7/12): "1862-Jul", 1862 + (10/12): "1862-Oct",
                            1863 + (1/12): "1863-Jan", 1863 + (4/12): "1863-Apr", 1863 + (7/12): "1863-Jul", 1863 + (10/12): "1863-Oct",
                            1864 + (1/12): "1864-Jan", 1864 + (4/12): "1864-Apr", 1864 + (7/12): "1864-Jul", 1864 + (10/12): "1864-Oct",
                            1865 + (1/12): "1865-Jan", maxtime: "1865-Apr"
                        }
                    ),
                ], style={'width': '76%', 'display': 'inline-block', 'vertical-align': 'top', 'margin': '1%'}),
                html.Div([
                    dcc.Graph(id="table"),
                    
                ], style={'width': '10%', 'display': 'inline-block', 'vertical-align': 'top', 'margin': '1%'})
            ]),
        ])
    ]),
])



@app.callback(
    Output(component_id='geomap', component_property='figure'),
    [Input(component_id='time-slider', component_property='value'),
    Input(component_id='dropdownPickType', component_property='value'),
    #Input('geomap', 'clickData')
    ]
)
def update_output(time, downdown_type):

    mydata = cwsac_battles.copy(deep=True)
    
    if time != [mintime, maxtime]:
        formatted_time_min_year = int(time[0])
        formatted_time_min_month = round((time[0] - int(time[0])) * 12)
        if (formatted_time_min_month == 0):
            formatted_time_min_year -= 1
            formatted_time_min_month = 12
        formatted_time_max_year = int(time[1])
        formatted_time_max_month = round((time[1] - int(time[1])) * 12)
        if (formatted_time_max_month == 0):
            formatted_time_max_year -= 1
            formatted_time_max_month = 12
        print(formatted_time_min_year, formatted_time_min_month, formatted_time_max_year, formatted_time_max_month)
        start_date = datetime(year=formatted_time_min_year, month=formatted_time_min_month, day=1)
        end_date = datetime(year=formatted_time_max_year, month=formatted_time_max_month, day=1)

        mydata = mydata[(mydata['start_date'] > start_date) & (mydata['start_date'] < end_date)]
        print(len(mydata))


    fig = px.scatter_mapbox(
        mydata,
        lat="lat",
        lon="long",
        color=downdown_type,
        mapbox_style="carto-positron",
        height=600,
        hover_name="battle_name",
        
        #size="strength",
        size_max=15,
        hover_data=["start_date", "end_date", "strength", "casualties"],
        zoom=3,
        title="Battle Locations")

    """fig.update_layout(
        mapbox = {
            'style': "white-bg",
            'center': {'lon': -86, 'lat': 35},
            'zoom': 3, 'layers': [{
                'source': usa_geojson,
                'type':'fill', 'below':'traces','color': 'grey', 'opacity' : 0.2}],
        },
        margin = {'l':0, 'r':0, 'b':0, 't':0})"""

    return fig

if __name__ == "__main__":  
    app.run_server(debug=True, port=8080)  # Turn off reloader if inside Jupyter