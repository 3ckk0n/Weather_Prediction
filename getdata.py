import requests
import datetime
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
def main():
    getHistoricalData_API()
    print("Đã lấy dữ liệu hoàn thành")
if __name__ == '__main__':
    main()
