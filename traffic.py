
from scipy import signal
import plotly.graph_objects as go
import ipywidgets as widgets
import pandas as pd
import numpy as np
from datetime import datetime
import plotly.express as px

import dash
from dash import dcc
from dash import html

def rgb_to_hex(r, g, b):
    return '#%02x%02x%02x' % (r, g, b)

WEEKDAYS = ["MONDAY", "TUESDAY", "WEDNESDAY", "THURSDAY", "FRIDAY", "SATURDAY", "SUNDAY"]

traffic_data2 = pd.read_csv("traffic_accidents_2018_pp.csv", encoding='utf-8')
traffic_data2.loc[traffic_data2["Number of Injuries"] >= 3, "Number of Injuries"] = "3+"
traffic_data2.loc[traffic_data2["Number of Motor Vehicles"] >= 4, "Number of Motor Vehicles"] = "4+"
traffic_data2.loc[
    (traffic_data2["Collision Type Description"] == "UNKNOWN") |
    (traffic_data2["Collision Type Description"] == "") |
    (traffic_data2["Collision Type Description"] == "Rear to Side") |
    (traffic_data2["Collision Type Description"] == "HEAD-ON") |
    (traffic_data2["Collision Type Description"] == "SIDESWIPE - OPPOSITE DIRECTION") |
    (traffic_data2["Collision Type Description"] == "REAR-TO-REAR"),
    "Collision Type Description"] = "Other"

categorical_dimensions = ['Illumination Description', 'Collision Type Description', "Number of Injuries", "Number of Motor Vehicles", 'Hit and Run']
#dim = dict(values=[WEEKDAYS[datetime.strptime(t[:10], "%d/%M/%Y").weekday()] for t in traffic_data["Date and Time"]], label="Weekday")
dimensions = [dict(values=traffic_data2[label], label=label) for label in categorical_dimensions]


# Build colorscale
traffic_data = pd.read_csv("traffic_accidents_2018_pp.csv", encoding='utf-8')
traffic_data.head()

#grouped_traffic_data = pd.DataFrame(traffic_data.groupby(by=['Hit and Run', "Collision Type Description"])["Number of Injuries"].sum())
grouped_traffic_data = pd.DataFrame(traffic_data.groupby(by=['Hit and Run', "Collision Type Description"]).agg({
    "Hit and Run": "first",
    "Collision Type Description": "first",
    "Number of Injuries": "sum",
}))
grouped_traffic_data2 = pd.DataFrame(traffic_data.groupby(by=['Hit and Run', "Illumination Description"]).agg({
    "Hit and Run": "first",
    "Illumination Description": "first",
    "Number of Injuries": "sum",
}))

# traffic_data

app = dash.Dash()

parcats_fig = go.FigureWidget(
    data=[
        go.Parcats(
            domain={'y': [0, 1]}, 
            dimensions=dimensions,
            line={
                'colorscale': [[0, 'gray'], [1, 'red']], 
                'color': [1 if t == "Y" else 0 for t in traffic_data["Hit and Run"]], 
                'shape': 'hspline'
            }
        )
    ]
)

app.layout = html.Div([
    html.Div(children=[
        dcc.Graph(id="graphParcat", 
            figure=parcats_fig
        ),
        html.Div(id="graphParcatDiv")
    ]),
    html.Div(children=[
        dcc.Graph(id="graphInjuriesByTime"),  # Injuries by time
        dcc.Dropdown(["Hour", "Week", "Month", "Year"], "Hour", id="picked_time")
    ]),
    html.Div(children=[
        dcc.Graph(#figure=go.FigureWidget([
            figure=px.bar(
                grouped_traffic_data, 
                x="Collision Type Description", 
                y="Number of Injuries", 
                color="Hit and Run", 
                barmode="relative")#, color="Collision Type Description"),
        ),
    ]),
    html.Div(children=[
        dcc.Graph(#figure=go.FigureWidget([
            figure=px.bar(
                grouped_traffic_data2, 
                x="Illumination Description", 
                y="Number of Injuries", 
                color="Hit and Run", 
                barmode="relative")#, color="Collision Type Description"),
        ),
    ]),
])

@app.callback(
    dash.Output('graphInjuriesByTime', 'figure'),
    dash.Input('picked_time', 'value'))
def update_injuries_by_time(selected):
    ymaxs = {"Hour": 400, "Week": 600, "Month": 500, "Year": 400}

    #fig = go.Histogram( # Scatter
    #    x=traffic_data[selected], 
    #    y=traffic_data["Number of Injuries"],
    #    nbinsx=300,
    #)
    
    #return go.FigureWidget(data=[fig], layout_yaxis_range=[0, ymaxs[selected]])

    fig = px.histogram( # Scatter
        traffic_data,
        x=selected,
        nbins=300,
        range_y=(0, ymaxs[selected]),
        color="Hit and Run"
        #color_discrete_sequence=[
        #    px.colors.sample_colorscale("reds", v)[0]
        #    for v in (
        #        traffic_data["Temperatur, Maximum"] / grouper["Temperatur, Maximum"].max()
        #    ).tolist()
        #],
        #color_discrete_sequence=[(222, 30, 30) for _ in range(len(traffic_data))]#[rgb_to_hex(222,30,30) for _ in range(len(traffic_data))]
        #y="Number of Injuries",
    )
    """
        def f(x):
        print(x)
        return "#ff0000"

    nbins = 250
    print(t for t in traffic_data[selected])
    print(traffic_data[selected][0])
    FORMAT_TO = f"%Y-%m-%d %H:%M:%S"
    
    t_max = max([datetime.timestamp(datetime.strptime(t, FORMAT_TO)) for t in list(traffic_data[selected])])

    count_injuries = [0] * nbins
    count_HR_Y = [0] * nbins
    count_HR_total = [0] * nbins
    time_dates = [0] * nbins
    for t, h_r, i_c in zip(traffic_data[selected], traffic_data["Hit and Run"], traffic_data["Number of Injuries"]):
        timestamp = datetime.timestamp(datetime.strptime(t, FORMAT_TO))
        idx = int((timestamp / (t_max + 1)) * nbins)

        count_HR_Y[idx] += (h_r == "Y")
        count_HR_total[idx] += 1
        count_injuries[idx] += i_c
        time_dates[idx] = t
    colors = [0] * nbins
    for i in range(nbins):
        if (count_HR_total[i] > 0):
            colors[i] = count_HR_Y[i] / count_HR_total[i]
        else:   
            colors[i] = 0

    fig = px.histogram( # Scatter
        x=time_dates,
        y=count_injuries,
        color_discrete_sequence=[px.colors.sample_colorscale("reds", c) for c in colors],
        nbins=250
        #color_discrete_sequence=[(222, 30, 30) for _ in range(len(traffic_data))]#[rgb_to_hex(222,30,30) for _ in range(len(traffic_data))]
        #y="Number of Injuries",
    )"""
    
    return fig#go.FigureWidget(data=[fig], layout_yaxis_range=[0, ymaxs[selected]])


# Define the callback function
@app.callback(
    dash.Output('graphParcat', 'figure'),
    [dash.Input('graphParcat', 'clickData')]
)
def update_output(points):
    #print(points)
    print("Updated")
    # Return the selected data as a string
    # Parcats figure
    new_color = np.zeros(len(traffic_data2), dtype='uint8')
    for a in points["points"]:
        new_color[a["pointNumber"]] = 1
        #new_color[a["pointNumber"]] = 1

    fig_parcat = go.FigureWidget(data=[go.Parcats(
        domain={'y': [0, 1]}, 
        dimensions=dimensions,
        line={
            'colorscale': [[0, 'gray'], [1, 'red']], 
            'color': new_color, 
            'shape': 'hspline'
        }
    )])
    return fig_parcat

if __name__ == "__main__":  
    app.run_server(debug=True, port=8080)  # Turn off reloader if inside Jupyter