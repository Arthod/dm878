
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
import dash_daq as daq
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
cwsac_commanders = pd.read_csv("dataset/cwsac_commanders.csv", encoding='utf-8')

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
                    html.H3(children="Focus",
                            style={'textAlign': 'left', 'font-family': 'Roboto, sans-serif', "padding-bottom": "2px"}),
                    dcc.Dropdown(["result", "campaign", "strength", "state_name", "theater"], "result", id="dropdownType"),

                    html.H3(children="Filters",
                            style={'textAlign': 'left', 'font-family': 'Roboto, sans-serif', "padding-bottom": "2px"}),
                    dcc.Dropdown(list(set(cwsac_battles["campaign"])), id="dropdownCampaigns", multi=True, placeholder="Select Campaign(s)",
                        style={"padding-bottom": "2px"}),
                    dcc.Dropdown(list(set(cwsac_battles["state_name"])), id="dropdownStates", multi=True, placeholder="Select State(s)"),
                    dcc.Dropdown(list(set(cwsac_battles["theater"])), id="dropdownTheaters", multi=True, placeholder="Select Theater(s)"),
                    dcc.Dropdown(list(set(cwsac_commanders["fullname"])), id="dropdownCommanders", multi=True, placeholder="Select Commander(s)"),
                    daq.ToggleSwitch(id="filterToggleSwitch", value=False),
                ], style={'width': '20%', 'display': 'inline-block', 'vertical-align': 'top', 'margin': '1%'}),
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
                    html.Div(id="placeholder", style={"display": "none"}),
                ], style={'width': '70%', 'display': 'inline-block', 'vertical-align': 'top', 'margin': '1%'}),
            ]),
        ]),
        html.Div(className='row', children=[
            html.Div([
                html.Div([
                    # Bloodiest Campaigns
                    dcc.Graph(id="battleCasualtiesByDate")
                ], style={'width': '33%', 'display': 'inline-block', 'vertical-align': 'top', 'margin': '0%'}),
                html.Div([   
                    dcc.Graph(id="campaignCasualtiesByDate")

                ], style={'width': '66%', 'display': 'inline-block', 'vertical-align': 'top', 'margin': '0%'}),
            ]),
        ]),
    ]),
])





@app.callback(
    [
        Output(component_id='geomap', component_property='figure'),
        Output(component_id='battleCasualtiesByDate', component_property='figure'),
        Output(component_id='campaignCasualtiesByDate', component_property='figure'),
    ],
    [
        Input(component_id='time-slider', component_property='value'),
        #Input(component_id='geomap', component_property='figure'),
        Input(component_id='dropdownType', component_property='value'),
        Input(component_id='dropdownCampaigns', component_property='value'),
        Input(component_id='dropdownStates', component_property='value'),
        Input(component_id='dropdownTheaters', component_property='value'),
        Input(component_id='dropdownCommanders', component_property='value'),
        Input(component_id="filterToggleSwitch", component_property="value")
    ]
)
def update_map(time, downdown_type, current_dropdown_campaigns, current_dropdown_states, current_dropdown_theaters, current_dropdown_commanders, filter_toggle_switch):

    mydata = cwsac_battles.copy(deep=True)

    print(current_dropdown_campaigns)
    print(current_dropdown_states)
    print(current_dropdown_theaters)
    print(current_dropdown_commanders)

    if (filter_toggle_switch):

        if (current_dropdown_campaigns is not None and len(current_dropdown_campaigns)):
            mydata = mydata[(mydata['campaign'].isin(current_dropdown_campaigns))]

        if (current_dropdown_states is not None and len(current_dropdown_states)):
            mydata = mydata[(mydata['state_name'].isin(current_dropdown_states))]

        if (current_dropdown_theaters is not None and len(current_dropdown_theaters)):
            mydata = mydata[(mydata['theater'].isin(current_dropdown_theaters))]

        if (current_dropdown_commanders is not None and len(current_dropdown_commanders)):
            mydata = mydata[
                (mydata['conf_commander1'].isin(current_dropdown_commanders)) | 
                (mydata['conf_commander2'].isin(current_dropdown_commanders)) | 
                (mydata['conf_commander3'].isin(current_dropdown_commanders)) | 
                (mydata['conf_commander4'].isin(current_dropdown_commanders)) | 

                (mydata['union_commander1'].isin(current_dropdown_commanders)) | 
                (mydata['union_commander2'].isin(current_dropdown_commanders)) | 
                (mydata['union_commander3'].isin(current_dropdown_commanders)) | 
                (mydata['union_commander4'].isin(current_dropdown_commanders))]


    
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


    fig1 = px.scatter_mapbox(
        mydata,
        lat="lat",
        lon="long",
        color=downdown_type,
        mapbox_style="carto-positron",
        height=600,
        hover_name="battle_name",
        symbol="campaign",
        
        #size="strength",
        size_max=15,
        hover_data=["start_date", "end_date", "strength", "casualties", "theater"],
        zoom=3,
        title="Battle Locations")


    fig2 = px.scatter(
        mydata,
        x="start_date",
        y="casualties",
        color=downdown_type,
        title="Casualties by date (Theater/Result)",
        )
    fig3 = px.scatter(
        mydata,
        x="start_date",
        y="casualties",
        color="campaign"
        )
    fig4 = px.scatter(
        mydata,
        x="start_date",
        y="strength",
        color="result"
        )

    return fig1, fig2, fig3




if __name__ == "__main__":  
    app.run_server(debug=True, port=8080)  # Turn off reloader if inside Jupyter