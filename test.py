import streamlit as st
import pandas as pd
import json
import requests
from plotly.subplots import make_subplots
import plotly.graph_objs as go
from datetime import datetime
import pytz
from timezonefinder import TimezoneFinder
import folium
from streamlit_folium import folium_static

# Set page configuration
st.set_page_config(page_title="Rain Prediction", page_icon=":umbrella_with_rain_drops:", layout="wide")

# Sample city coordinates
lat = 40.7128  # Latitude for New York (change to the selected city's lat)
lng = -74.0060  # Longitude for New York (change to the selected city's lng)
city = "New York"  # City name
country = "USA"  # Country name

st.subheader("Week ahead")
st.write('Temperature and rain forecast for the week ahead & city location on the map', unsafe_allow_html=True)

# Fetch weather data
with st.spinner('Loading...'):
    response_hourly = requests.get(f'https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lng}&hourly=temperature_2m,precipitation')
    result_hourly = json.loads(response_hourly._content)
    hourly = result_hourly["hourly"]
    hourly_df = pd.DataFrame.from_dict(hourly)
    
    hourly_df.rename(columns={'time': 'Week ahead', 'temperature_2m': 'Temperature °C', 'precipitation': 'Precipitation mm'}, inplace=True)
    
    # Use timezonefinder to get the timezone based on latitude and longitude
    tf = TimezoneFinder()
    timezone_str = tf.timezone_at(lng=lng, lat=lat)
    
    # Get the timezone and offset
    timezone_loc = pytz.timezone(timezone_str)
    dt = datetime.now()
    tzoffset = timezone_loc.utcoffset(dt)
    
    # Convert time
    week_ahead = pd.to_datetime(hourly_df['Week ahead'], format="%Y-%m-%dT%H:%M")
    
    # Create figure with dual y-axis
    fig = make_subplots(specs=[[{"secondary_y": True}]])

    # Add temperature trace
    fig.add_trace(go.Scatter(x=week_ahead + tzoffset,
                             y=hourly_df['Temperature °C'],
                             name="Temperature °C"),
                  secondary_y=False)

    # Add precipitation trace
    fig.add_trace(go.Bar(x=week_ahead + tzoffset,
                         y=hourly_df['Precipitation mm'],
                         name="Precipitation mm"),
                  secondary_y=True)
    
    # Add a vertical line to indicate the current time
    time_now = datetime.now(pytz.utc) + tzoffset
    fig.add_vline(x=time_now, line_color="red", opacity=0.4)
    fig.add_annotation(x=time_now, y=max(hourly_df['Temperature °C']) + 5,
                       text=time_now.strftime("%d %b %y, %H:%M"),
                       showarrow=False,
                       yshift=0)

    # Update y-axis ranges
    fig.update_yaxes(range=[min(hourly_df['Temperature °C']) - 10,
                            max(hourly_df['Temperature °C']) + 10],
                     title_text="Temperature °C",
                     secondary_y=False,
                     showgrid=False,
                     zeroline=False)

    fig.update_yaxes(range=[min(hourly_df['Precipitation mm']) - 2,
                            max(hourly_df['Precipitation mm']) + 8],
                     title_text="Precipitation (mm)",
                     secondary_y=True,
                     showgrid=False)

    # Update layout
    fig.update_layout(legend=dict(
        orientation="h",
        yanchor="bottom",
        y=1.02,
        xanchor="right",
        x=0.7
    ))

    # Create the map using Folium
    m = folium.Map(location=[lat, lng], zoom_start=7)
    folium.Marker([lat, lng],
                  popup=f"{city}, {country}",
                  tooltip=f"{city}, {country}").add_to(m)

    # Make the map responsive
    make_map_responsive = """
    <style>
    [title~="st.iframe"] { width: 100%}
    </style>
    """
    st.markdown(make_map_responsive, unsafe_allow_html=True)

    # Display the forecast chart
    st.plotly_chart(fig, use_container_width=True)

    # Display the map
    st_data = folium_static(m, height=370)
