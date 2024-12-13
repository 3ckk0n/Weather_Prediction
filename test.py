import streamlit as st
import pandas as pd
import requests
import json
from plotly.subplots import make_subplots
import plotly.graph_objs as go
from datetime import datetime
import pytz
from timezonefinder import TimezoneFinder  # Use timezonefinder instead of tzwhere
import folium
from streamlit_folium import folium_static
from getdata import getCurrentData, getlabel, getFuturelabel
import pickle
# Set page config
st.set_page_config(page_title="Weather Prediction", page_icon=":umbrella_with_rain_drops:", layout="wide")

# Load the custom CSS file into the Streamlit app
def load_css():
    with open("style/styles.css") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
# Apply the CSS file
load_css()

# Thematic Header
html_templ = """
    <div style="background-color:#2D3E50; padding:20px; text-align:center; border-radius:10px;">
        <h1 style="color:white; font-family: 'Arial', sans-serif; font-size: 36px;">
            <span style="font-size: 50px; vertical-align: middle;">&#9748;</span> 
            Rain Prediction, <span style="color:#ffeb3b;">&#9748;</span>
        </h1>
        <p style="color:white; font-size: 18px; font-family: 'Arial', sans-serif; font-weight: 300;">
            A comprehensive web application for predicting rainfall and weather conditions.
        </p>
    </div>
    """
st.markdown(html_templ, unsafe_allow_html=True)

# Sidebar context with improvements for design
st.sidebar.title("Weather Prediction Sidebar")
st.sidebar.header("Choose the content")
content_choice = st.sidebar.selectbox("Choose the state", ("Weather Station", "Weather Prediction Model"))

# Load city data
file = "worldcities.csv"
data = pd.read_csv(file)

# Add custom CSS for font size styling for selectbox components
st.markdown("""
    <style>
    .stSelectbox>div>div>div>label {
        font-size: 18px !important; /* Font size for selectbox label */
    }
    .stSelectbox>div>div>div>div>div>div {
        font-size: 16px !important; /* Font size for selectbox options */
    }
    .stButton>button {
        font-size: 16px !important; /* Button font size */
    }
    .stMarkdown {
        font-size: 16px !important; /* Markdown text font size */
    }
    </style>
    """, unsafe_allow_html=True)

if content_choice == "Weather Station":
    st.subheader("Weather Station")
    
    # Select Country
    country_set = set(data.loc[:, "country"])
    country = st.selectbox('Select a country', options=country_set )

    country_data = data.loc[data.loc[:, "country"] == country, :]
    city_set = country_data.loc[:, "city_ascii"]
    city = st.selectbox('Select a city', options=city_set)

    lat = float(country_data.loc[data.loc[:, "city_ascii"] == city, "lat"])
    lng = float(country_data.loc[data.loc[:, "city_ascii"] == city, "lng"])

    # Get current weather data from Open Meteo API
    response_current = requests.get(f'https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lng}&current_weather=true')
    data, label = getCurrentData(lat,lng)
    # Load model
    # load
    with open('decision_tree.pkl', 'rb') as f:
        clf = pickle.load(f)
    # Predict the result
    result = clf.predict(data)
    label_temp = getlabel(result[0])

    # Display the selected location in the sidebar
    st.write(f"Selected Location: {city}, {country}")

    # Get temperature unit
    units = st.selectbox("Select Temperature Unit: ", ('celsius', 'fahrenheit'))
    degree = 'C' if units == 'celsius' else 'F'

    # Display current weather
    result_current = json.loads(response_current._content)
    current = result_current["current_weather"]
    temp = current["temperature"]
    speed = current["windspeed"]
    direction = current["winddirection"]

    # Determine wind direction
    ddeg = 11.25
    direction_dict = {
        0: "N", 337.5: "N/NW", 315: "NW", 292.5: "W/NW", 270: "W", 247.5: "W/SW", 225: "SW",
        202.5: "S/SW", 180: "S", 157.5: "S/SE", 135: "SE", 112.5: "E/SE", 90: "E", 67.5: "E/NE",
        45: "NE", 22.5: "N/NE"
    }

    # Wind direction logic
    common_dir = ""
    for angle, dir_name in direction_dict.items():
        if direction >= (angle - ddeg) and direction < (angle + ddeg):
            common_dir = dir_name
            break

    st.info(f"The current temperature is {temp} °{degree}. \nThe wind speed is {speed} m/s. \nThe wind is coming from {common_dir}.")
    st.info(f"The current weather condition will be : {label_temp.iloc[0]["day"]}")
    # Fetch hourly data for the week ahead
    st.subheader("Week ahead")
    st.write('Temperature and rain forecast one week ahead & city location on the map')

    with st.spinner('Loading...'):
        response_hourly = requests.get(f'https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lng}&hourly=temperature_2m,precipitation')
        result_hourly = json.loads(response_hourly._content)
        hourly = result_hourly["hourly"]
        hourly_df = pd.DataFrame.from_dict(hourly)
        hourly_df.rename(columns={'time': 'Week ahead', 'temperature_2m': 'Temperature °C', 'precipitation': 'Precipitation mm'}, inplace=True)
        
        # Use timezonefinder to get the timezone
        tf = TimezoneFinder()
        timezone_str = tf.timezone_at(lng=lng, lat=lat)

        # Convert time to local time zone
        timezone_loc = pytz.timezone(timezone_str)
        dt = datetime.now()
        tzoffset = timezone_loc.utcoffset(dt)
        
        # Plot temperature and precipitation
        fig = make_subplots(specs=[[{"secondary_y": True}]])

        # Convert 'Week ahead' to datetime and apply timezone
        week_ahead = pd.to_datetime(hourly_df['Week ahead'], format="%Y-%m-%dT%H:%M")

        # Add temperature trace
        fig.add_trace(go.Scatter(x=week_ahead + tzoffset, y=hourly_df['Temperature °C'], name="Temperature °C"), secondary_y=False)
        # Add precipitation trace
        fig.add_trace(go.Bar(x=week_ahead + tzoffset, y=hourly_df['Precipitation mm'], name="Precipitation mm"), secondary_y=True)

        # Add vertical line for current time
        time_now = datetime.now(pytz.utc) + tzoffset
        fig.add_vline(x=time_now, line_color="red", opacity=0.4)
        fig.add_annotation(x=time_now, y=max(hourly_df['Temperature °C']) + 5, text=time_now.strftime("%d %b %y, %H:%M"), showarrow=False, yshift=0)
        
        # Update y-axes
        fig.update_yaxes(range=[min(hourly_df['Temperature °C']) - 10, max(hourly_df['Temperature °C']) + 10], title_text="Temperature °C", secondary_y=False, showgrid=False, zeroline=False)
        fig.update_yaxes(range=[min(hourly_df['Precipitation mm']) - 2, max(hourly_df['Precipitation mm']) + 8], title_text="Precipitation (rain/showers/snow) mm", secondary_y=True, showgrid=False)

        # Layout adjustments
        fig.update_layout(legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=0.7))

        # Display map
        m = folium.Map(location=[lat, lng], zoom_start=7)
        folium.Marker([lat, lng], popup=city + ', ' + country, tooltip=city + ', ' + country).add_to(m)
        folium_static(m, height=370)

        # Display chart
        st.plotly_chart(fig, use_container_width=True)

else:
    st.subheader("Weather Prediction Model")

    # Select Country
    country_set = set(data.loc[:, "country"])
    country = st.selectbox('Select a country', options=country_set )

    country_data = data.loc[data.loc[:, "country"] == country, :]
    city_set = country_data.loc[:, "city_ascii"]
    city = st.selectbox('Select a city', options=city_set)

    lat = float(country_data.loc[data.loc[:, "city_ascii"] == city, "lat"])
    lng = float(country_data.loc[data.loc[:, "city_ascii"] == city, "lng"])
    temp_df,label = getFuturelabel()
    with open('decision_tree.pkl', 'rb') as f:
        clf = pickle.load(f)
    # Predict the result
    result = clf.predict(temp_df)
    label_temp = []
    for i in range(7):
        label_temp.append(getlabel(result[0]))

    # Get current weather data from Open Meteo API
    response_current = requests.get(f'https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lng}&current_weather=true')
    # data, label = getCurrentData(lat,lng)
    # # Load model
    # # load
    # with open('decision_tree.pkl', 'rb') as f:
    #     clf = pickle.load(f)
    # # Predict the result
    # result = clf.predict(data)
    # label_temp = getlabel(result[0])

    # Display the selected location in the sidebar
    st.write(f"Selected Location: {city}, {country}")

    # Get temperature unit
    units = st.selectbox("Select Temperature Unit: ", ('celsius', 'fahrenheit'))
    degree = 'C' if units == 'celsius' else 'F'

    # Display current weather
    result_current = json.loads(response_current._content)
    current = result_current["current_weather"]
    temp = current["temperature"]
    speed = current["windspeed"]
    direction = current["winddirection"]

    # Determine wind direction
    ddeg = 11.25
    direction_dict = {
        0: "N", 337.5: "N/NW", 315: "NW", 292.5: "W/NW", 270: "W", 247.5: "W/SW", 225: "SW",
        202.5: "S/SW", 180: "S", 157.5: "S/SE", 135: "SE", 112.5: "E/SE", 90: "E", 67.5: "E/NE",
        45: "NE", 22.5: "N/NE"
    }

    # Wind direction logic
    common_dir = ""
    for angle, dir_name in direction_dict.items():
        if direction >= (angle - ddeg) and direction < (angle + ddeg):
            common_dir = dir_name
            break

    st.info(f"The current temperature is {temp} °{degree}. \nThe wind speed is {speed} m/s. \nThe wind is coming from {common_dir}.")
    for i in range(7):
        st.info(f"The predict in next {i} days weather condition will be : {label_temp[i]}")
    # Fetch hourly data for the week ahead
    st.subheader("Week ahead")
    st.write('Temperature and rain forecast one week ahead & city location on the map')

    with st.spinner('Loading...'):
        response_hourly = requests.get(f'https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lng}&hourly=temperature_2m,precipitation')
        result_hourly = json.loads(response_hourly._content)
        hourly = result_hourly["hourly"]
        hourly_df = pd.DataFrame.from_dict(hourly)
        hourly_df.rename(columns={'time': 'Week ahead', 'temperature_2m': 'Temperature °C', 'precipitation': 'Precipitation mm'}, inplace=True)

        # Use timezonefinder to get the timezone
        tf = TimezoneFinder()
        timezone_str = tf.timezone_at(lng=lng, lat=lat)

        # Convert time to local time zone
        timezone_loc = pytz.timezone(timezone_str)
        dt = datetime.now()
        tzoffset = timezone_loc.utcoffset(dt)
        
        # Plot temperature and precipitation
        fig = make_subplots(specs=[[{"secondary_y": True}]])

        # Convert 'Week ahead' to datetime and apply timezone
        week_ahead = pd.to_datetime(hourly_df['Week ahead'], format="%Y-%m-%dT%H:%M")

        # Add temperature trace
        fig.add_trace(go.Scatter(x=week_ahead + tzoffset, y=hourly_df['Temperature °C'], name="Temperature °C"), secondary_y=False)
        # Add precipitation trace
        fig.add_trace(go.Bar(x=week_ahead + tzoffset, y=hourly_df['Precipitation mm'], name="Precipitation mm"), secondary_y=True)

        # Add vertical line for current time
        time_now = datetime.now(pytz.utc) + tzoffset
        fig.add_vline(x=time_now, line_color="red", opacity=0.4)
        fig.add_annotation(x=time_now, y=max(hourly_df['Temperature °C']) + 5, text=time_now.strftime("%d %b %y, %H:%M"), showarrow=False, yshift=0)
        
        # Update y-axes
        fig.update_yaxes(range=[min(hourly_df['Temperature °C']) - 10, max(hourly_df['Temperature °C']) + 10], title_text="Temperature °C", secondary_y=False, showgrid=False, zeroline=False)
        fig.update_yaxes(range=[min(hourly_df['Precipitation mm']) - 2, max(hourly_df['Precipitation mm']) + 8], title_text="Precipitation (rain/showers/snow) mm", secondary_y=True, showgrid=False)

        # Layout adjustments
        fig.update_layout(legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=0.7))

        # Display map
        m = folium.Map(location=[lat, lng], zoom_start=7)
        folium.Marker([lat, lng], popup=city + ', ' + country, tooltip=city + ', ' + country).add_to(m)
        folium_static(m, height=370)


# Create empty space at the top so the "About the Author" button appears at the bottom
st.sidebar.empty()  # This creates some space

# About the Author section at the bottom of the sidebar
if st.sidebar.button("About the Author"):
    st.sidebar.subheader("Weather Prediction App")
    st.sidebar.markdown("by PhuongNgo")
    st.sidebar.markdown("[ngop2515@gmail.com]")
    st.sidebar.text("All Rights Reserved (2024)")

# Sidebar References section
st.sidebar.markdown("References")
st.sidebar.markdown("https://github.com/3ckk0n/Weather_Prediction")
