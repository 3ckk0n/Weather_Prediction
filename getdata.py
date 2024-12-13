import requests
import datetime
import pandas as pd
from sklearn.preprocessing import LabelEncoder
from pandas.api.types import is_numeric_dtype
import numpy as np
# from datetime import date
import json
def getHistoricalData_API():
    # Get current date
    start_date = datetime.date(2024, 1, 1)
    end_date = datetime.date.today()
    # delta time
    delta = datetime.timedelta(days=1)
    # Iterate from date to date
    while (start_date <= end_date):
        # Get historical data by date
        response = requests.get("http://api.weatherapi.com/v1/history.json?key=##########################&q=Saigon&dt=" + str(start_date))
        if response.status_code == 200:
            # Get json data from request
            data = response.json()
            # json_object = json.dumps(data, indent=4)
            data = json.dumps(data, indent = 4, sort_keys=True)
            # Save to data directory, "wb" mode Open the file for writing in binary format.
            # Truncates the file if it already exists. Creates a new file if it does not exist.
            with open ("./data/" + str(start_date) + ".json", "w") as file:
                # Serializing json
                file.write(data)
            start_date += delta
def getCurrentData(lat,lon):
    # Get current date
    today = datetime.date.today()
    response = requests.get("https://api.weatherapi.com/v1/current.json?key=aa22924bef8642b1b20151204242711&q=${str(lat)},${str(lon)}&aqi=no")
    if response.status_code == 200:
        # Get json data from request
        data = response.json()
        data = data["current"]
        temp_df = pd.json_normalize(data)
        data = temp_df[["temp_c","temp_f","is_day","wind_mph","wind_kph","wind_degree","wind_dir","pressure_mb","pressure_in","precip_mm","precip_in","humidity","cloud","feelslike_c","feelslike_f","windchill_c","windchill_f","heatindex_c","heatindex_f","dewpoint_c","dewpoint_f","vis_km","vis_miles","uv","gust_mph","gust_kph"]]
        label = temp_df["condition.code"]
        encoder = LabelEncoder()
        encoder.classes_ = np.load('./classes.npy', allow_pickle=True)
        for column in data.columns:
            # Only encoder categorical or numerical
            if not is_numeric_dtype(data[column]):
                data[column] = encoder.fit_transform(data[column])
        return data, label
def getlabel(code):
    label = pd.read_csv("./weather_conditions.csv")
    temp = label[label['code'] == code]
    return temp
def getFuturelabel():
    response = requests.get("https://api.weatherapi.com/v1/forecast.json?key=aa22924bef8642b1b20151204242711&q=Saigon&days=7&aqi=no&alerts=no")
    if response.status_code == 200:
        # Get json data from request
        data = response.json()
        # json_object = json.dumps(data, indent=4)
        data = json.dumps(data, indent = 4, sort_keys=True)
        # Save to data directory, "wb" mode Open the file for writing in binary format.
        # Truncates the file if it already exists. Creates a new file if it does not exist.
        with open ("./future/" + str(datetime.date.today()) + ".json", "w") as file:
            # Serializing json
            file.write(data)
        # Reading from json file
        json_object = pd.read_json("./future/" + str(datetime.date.today()) + ".json")
        # We only need data in "hour"
        json_object = json_object['forecast']['forecastday'].pop(0)
        json_object = json_object["hour"]
        temp_data = pd.DataFrame()
        for i in range(7):
            temp_df = pd.json_normalize(json_object[i])
            temp_data = pd.concat([temp_data,temp_df])
        
        data = temp_df[["temp_c","temp_f","is_day","wind_mph","wind_kph","wind_degree","wind_dir","pressure_mb","pressure_in","precip_mm","precip_in","humidity","cloud","feelslike_c","feelslike_f","windchill_c","windchill_f","heatindex_c","heatindex_f","dewpoint_c","dewpoint_f","vis_km","vis_miles","uv","gust_mph","gust_kph"]]
        label = temp_df["condition.code"]
        encoder = LabelEncoder()
        encoder.classes_ = np.load('./classes.npy', allow_pickle=True)
        for column in data.columns:
            # Only encoder categorical or numerical
            if not is_numeric_dtype(data[column]):
                data[column] = encoder.fit_transform(data[column])
        return data, label
    else:
        print("Error")
# def main():
#     getCurrentData(10.869418,106.803374)
#     print("Đã lấy dữ liệu hoàn thành")
# if __name__ == '__main__':
#     main()
