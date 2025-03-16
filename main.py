import json
import os
import requests
import datetime
from datetime import datetime, timedelta
import pytz
from tzlocal import get_localzone
from timezonefinder import TimezoneFinder
import calendar
import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
from tkinter import PhotoImage
from PIL import Image, ImageTk
from io import BytesIO


class Weather_App(tk.Tk):

    def __init__(self):

        # Main setup
        super().__init__()
        self.title("Weather App")
        self.geometry("800x500")
        self.grid()
        self.rowconfigure(0, weight=2, uniform="a")
        self.rowconfigure(1, weight=8, uniform="a")
        self.rowconfigure(2, weight=5, uniform="a")
        self.columnconfigure(0, weight=1, uniform="a")
        self.columnconfigure(1, weight=1, uniform="a")
        self.columnconfigure(2, weight=2, uniform="a")
        self.configure(bg="#003049")
        self.resizable(False,False)

        # Main weather icon canvas
        self.main_weather_icon_canvas = tk.Canvas(self, background = "#003049", bd=0, highlightthickness=0, relief="ridge")
        self.main_weather_icon_canvas.grid(row=1, column=0, sticky="nsew", padx=20, pady=20)

        # Initial image canvas
        self.initial_image_canvas = tk.Canvas(self, background = "#003049", bd=0, highlightthickness=0, relief="ridge")
        self.initial_image_canvas.grid(row=0, column=0, rowspan=3, columnspan=3, sticky="nsew")

        # Widgets
        self.GUI_search_bar()
        self.credentials()

        # Binding
        self.initial_image_canvas.bind("<Configure>", self.display_initial_image)
        self.textfield.bind("<Return>", self.execute_search)

        # Running
        self.mainloop()

    def credentials(self):
        ''' Gets the credentials to the tomorrow.io API from a JSON file '''

        global credentials
        try:
            with open("/Users/katia/Python Projects/Weather App/tomorrow_io_credentials.json") as credentials_file:
                credentials = json.load(credentials_file)
        except FileNotFoundError:
            print('File not found')
    
    def API_request(self, credentials):
        ''' Sends the API request, receives a response and transforms the response into a Python dictionary '''

        global current_weather, daily_forecast

        # Getting the API responses
        apikey = credentials['apikey']
        location = self.textfield.get()
        url_realtime = f"https://api.tomorrow.io/v4/weather/realtime?location={location}&apikey={apikey}"
        url_forecast = f"https://api.tomorrow.io/v4/weather/forecast?location={location}&apikey={apikey}"
        response_realtime = requests.get(url_realtime)
        response_forecast = requests.get(url_forecast)

        # Converting the responses from JSON format
        if response_realtime.status_code == 200 and response_forecast.status_code == 200:
            current_weather = response_realtime.json()
            daily_forecast = response_forecast.json()["timelines"]["daily"]
            return current_weather, daily_forecast
        
        # Displaying error messages
        elif response_realtime.status_code == 429 or response_forecast.status_code == 429:
            self.show_error_popup(message="Rate limit reached, please try again later (after the full hour).")
        else:
            self.show_error_popup(message="Location not found, please try again.")

    def show_error_popup(self, message):
        ''' Shows error popup, in case that the API request was not succesful '''

        messagebox.showerror("Error", message)

    def get_current_weather(self, current_weather, daily_forecast):
        ''' Saves current weather data from the Python dictionary, assigns the correct weather description based on the weather code '''

        global timezone, current_weather_code, current_temperature_c, current_apparent_temperature_c, current_wind_speed, current_humidity, current_cloud_cover, current_precipitation_probability, current_location, current_state, current_weather_description, formatted_current_date, local_time, day_of_week, timezone, current_time_utc, weather_data, local_data_time_info

        # Defining whether it is day or night right now
        current_time_utc = current_weather["data"]["time"]
        sunrise_time = daily_forecast[0]["values"]["sunriseTime"]
        sunset_time = daily_forecast[0]["values"]["sunsetTime"]
        if current_time_utc < sunrise_time or current_time_utc > sunset_time:
            current_state = 1       # 1 is night
        else:
            current_state = 0       # 0 is day

        # Loading corresponding weather descriptions from the JSON file
        weather_codes_url = "https://raw.githubusercontent.com/xKatyJane/Weather_app/refs/heads/main/Data/weather_codes.json"
        response_weather_data = requests.get(weather_codes_url)
        weather_data = response_weather_data.json()
        weather_codes_day = weather_data["weatherCodeDay"]
        weather_codes_night = weather_data["weatherCodeNight"]

        # Defining the weather descriptions based on the current_state (day or night)
        current_weather_code = int(str(current_weather["data"]["values"]["weatherCode"])+str(current_state))
        if current_state == 1:
            current_weather_description = weather_codes_night.get(str(current_weather_code), "Unknown")
        elif current_state == 0:
            current_weather_description = weather_codes_day.get(str(current_weather_code), "Unknown")
        else:
            current_weather_description = "Unknown"
        
        # Extracting the weather data
        current_location_original = current_weather["location"]["name"].split(",")
        current_location = ",".join([current_location_original[0], current_location_original[-1]])
        current_temperature_c = current_weather["data"]["values"]["temperature"]
        current_apparent_temperature_c = current_weather["data"]["values"]["temperatureApparent"]
        current_wind_speed = current_weather["data"]["values"]["windSpeed"]
        current_humidity = current_weather["data"]["values"]["humidity"]
        current_cloud_cover = current_weather["data"]["values"]["cloudCover"]
        current_precipitation_probability = current_weather["data"]["values"]["precipitationProbability"]
        latitude = current_weather["location"]["lat"]
        longitude = current_weather["location"]["lon"]

        # Finding the local time, current date and day of the week
        tf = TimezoneFinder()
        timezone_str = tf.timezone_at(lng=longitude, lat=latitude)
        timezone = pytz.timezone(timezone_str)
        local_data_time_info = datetime.now(timezone)
        current_date = local_data_time_info.date()
        formatted_current_date = current_date.strftime("%d %B %Y")
        local_time = local_data_time_info.time().isoformat('seconds')
        day_of_week = local_data_time_info.strftime("%A")

    def get_weather_next_days(self, daily_forecast, weather_data):
        ''' Saves weather data for the next five days from the Python dictionary '''
        global temperatures, weather_codes, next_days_of_the_week

        # Creating empty lists
        temperatures = []
        weather_codes = []
        next_days_of_the_week = []

        # Weather descriptions from the JSON file
        weather_codes_forecast = weather_data["weatherCodeFullDay"]

        # Defining data for the next 5 days
        for i in range (1, 6):
            avg_temp_c = daily_forecast[i]["values"]["temperatureAvg"]
            weather_code = int(str(daily_forecast[i]["values"]["weatherCodeMax"]) + str("0"))
            next_day_date = daily_forecast[i]["time"]
            next_day_datetime = datetime.fromisoformat(next_day_date.replace("Z", "+00:00"))
            offset = local_data_time_info.strftime("%z")
            sign = 1 if offset[0] == "+" else -1
            hours_td = int(offset[1:3])
            minutes_td = int(offset[3:])
            time_delta = timedelta(hours=hours_td * sign, minutes=minutes_td * sign)
            next_day_local_time = next_day_datetime + time_delta
            next_day_of_week = next_day_local_time.strftime("%A")

            temperatures.append(avg_temp_c)
            weather_codes.append(weather_code)
            next_days_of_the_week.append(next_day_of_week)

    def execute_search(self, event=None):
        ''' Function activated on clicking the SEARCH button '''

        self.API_request(credentials)
        self.get_current_weather(current_weather, daily_forecast)
        self.get_weather_next_days(daily_forecast, weather_data)
        self.GUI_current_weather_icon(current_weather_code)
        self.GUI_current_temperarture(current_temperature_c, current_apparent_temperature_c, current_weather_description)
        self.GUI_current_weather_details(current_location, day_of_week, formatted_current_date, local_time, current_wind_speed, current_cloud_cover, current_humidity, current_precipitation_probability)
        self.GUI_five_days_labels(temperatures, weather_codes, next_days_of_the_week)
        self.hide_initial_image()
        
    def display_initial_image(self, event):
        ''' Displays the initial image, before any weather data is loaded '''

        width = event.width
        height = event.height
        self.initial_image_url = "https://raw.githubusercontent.com/xKatyJane/Weather_app/main/Assets/Images/Initial_image.png"
        self.response_initial_image = requests.get(self.initial_image_url)
        self.initial_img_data = BytesIO(self.response_initial_image.content)
        self.initial_image = Image.open(self.initial_img_data)
        self.resized_initial_image = self.initial_image.resize((width, height))
        self.resized_initial_image_tk = ImageTk.PhotoImage(self.resized_initial_image)
        self.initial_image_canvas.create_image(0,0, image=self.resized_initial_image_tk, anchor="nw")

    def hide_initial_image(self):
        ''' Hides the initial image after weather data is displayed '''

        self.initial_image_canvas.grid_forget()

    def GUI_search_bar(self):
        ''' Configuration of the search bar '''

        # The search bar
        search_bar = tk.Frame(self, bg="#003049")
        search_bar.grid(row = 0, column = 0, columnspan=2, sticky="nsew")
        search_bar.rowconfigure(0, weight=1, uniform="a")
        search_bar.columnconfigure(0, weight=5, uniform="a")
        search_bar.columnconfigure(1, weight=1, uniform="a")

        # Entry field and search button
        self.textfield = tk.Entry(search_bar, justify="left", border=2, bg="#caf0f8", fg="black", font=("Montserrat", 18), insertbackground="black", insertwidth=2)
        self.textfield.focus()
        self.textfield.grid(row = 0, column = 0, sticky="nsew", padx=(5,0), pady=5)
        search_button = tk.Button(search_bar, text="search", command=self.execute_search)
        search_button.grid(row = 0, column = 1, sticky="nsew", padx=(0,5), pady=5)
        
    def GUI_current_weather_icon(self, current_weather_code):
        ''' Assigns the correct weather icon, based on the weather code '''

        # The main weather icon
        current_main_weather_icon_path = f"https://raw.githubusercontent.com/xKatyJane/Weather_app/main/Assets/Weather_icons/{current_weather_code}.png"
        response_main_weather_icon = requests.get(current_main_weather_icon_path)
        main_weather_img_data = BytesIO(response_main_weather_icon.content)
        original_main_weather_icon = Image.open(main_weather_img_data).resize((130, 130), Image.Resampling.LANCZOS)
        main_weather_icon_tk = ImageTk.PhotoImage(original_main_weather_icon)
        self.main_weather_icon_canvas.create_image((70, 100), anchor="center", image=main_weather_icon_tk)
        self.initial_image_canvas.image = main_weather_icon_tk

    def GUI_current_temperarture(self, current_temperature_c, current_apparent_temperature_c, current_weather_description):
        ''' Configuration and display of the current weather data (temperature, apparent temperature, description) '''

        # Frame
        temp_conditions_frame = tk.Frame(self, bg="#003049", bd=0, highlightthickness=0, relief="ridge")
        temp_conditions_frame.grid(row = 1, column = 1, sticky="nsew")
        temp_conditions_frame.rowconfigure((0, 1, 2), weight=1, uniform="a")
        temp_conditions_frame.columnconfigure(0, weight=1, uniform="a")

        # Current temperature and conditions
        current_temperature_label = tk.Label(temp_conditions_frame, text=f"{current_temperature_c} °C", font=("Montserrat", 35, "bold"), fg="#fefae0", bg="#003049")
        current_temperature_label.grid(row = 0, column = 0, sticky="sew", pady=(30,0))
        feels_like_label = tk.Label(temp_conditions_frame, text=f"Feels like {current_apparent_temperature_c}", font=("Montserrat", 25), fg="#ffb703", bg="#003049")
        feels_like_label.grid(row = 1, column = 0, sticky="nsew")
        current_description_label = tk.Label(temp_conditions_frame, text=current_weather_description, font=("Montserrat", 20), bg="#003049")
        current_description_label.grid(row = 2, column = 0, sticky="new", pady=(0,30))
    
    def GUI_current_weather_details(self, current_location, day_of_week, formatted_current_date, local_time, current_wind_speed, current_cloud_cover, current_humidity, current_precipitation_probability):
        ''' Configuration and display of the current time, date and weather details: wind speed, cloud cover, humidity, precipitation probability '''

        # Current location
        current_location_label = tk.Label(self, text=current_location, font=("Raleway", 18, "bold"), fg="#ffb703", bg="#003049", wraplength=350)
        current_location_label.grid(row = 0, column = 2, sticky="nsew", padx=10, pady=10)

        # current weather label
        current_conditions_label = tk.Frame(self, bg="#003049", bd=0, highlightthickness=0, relief="ridge")
        current_conditions_label.grid(row = 1, column = 2, sticky="nsew")
        current_conditions_label.rowconfigure((0, 1, 2), weight=1, uniform="a")
        current_conditions_label.columnconfigure(0, weight=1, uniform="a")

        # Frame: current time and date / weather details
        current_frame = tk.Frame(self, bg="#003049")
        current_frame.grid(row = 1, column = 2, sticky="nsew")
        current_frame.rowconfigure(0, weight=1, uniform="a")
        current_frame.rowconfigure(1, weight=2, uniform="a")
        current_frame.columnconfigure(0, weight=1, uniform="a")

        # Current time and date / weather details
        current_date_and_time_label = tk.Label(current_frame, text=f"{day_of_week}, {formatted_current_date}\n\nLocal time: {local_time}", font=("Montserrat", 17), bg="#003049", justify="left", anchor="w")
        current_date_and_time_label.grid(row = 0, column = 0, sticky="nsew", padx=40, pady=(10, 5))
        current_weather_details_label = tk.Label(current_frame, text=f"Wind speed: {current_wind_speed} m/s\n\nCloud cover: {current_cloud_cover} %\n\nHumidity: {current_humidity} %\n\nPrecipitation probability: {current_precipitation_probability} %", font=("Montserrat", 17), bg="#003049", justify="left", anchor="w")
        current_weather_details_label.grid(row = 1, column = 0, sticky="nsew", padx=40, pady=(10, 20))

    def GUI_five_days_labels(self, temperatures, weather_codes, next_days_of_the_week):
        ''' Configuration and display of the weather data for the next five days '''

        # Frame for the 5 day labels
        next_days_weather_frame =  tk.Frame(self, background = "#003049", bd=0, highlightthickness=0, relief="ridge")
        next_days_weather_frame.grid(row = 2, column = 0, columnspan = 3, sticky="nsew")
        next_days_weather_frame.rowconfigure(0, weight=1, uniform="a")
        next_days_weather_frame.columnconfigure((0, 1, 2, 3, 4), weight=1, uniform="a")

        # Loop to create the data inside the main frame
        for i in range (5):

            # Day frames
            day_frame = tk.Frame(next_days_weather_frame, background = "#219ebc", bd=5, highlightthickness=0, relief="solid")
            day_frame.grid(row = 0, column = i, rowspan = 3, sticky="nsew", padx=5, pady=5)
            day_frame.rowconfigure(0, weight=3, uniform="a")
            day_frame.rowconfigure(1, weight=1, uniform="a")
            day_frame.rowconfigure(2, weight=1, uniform="a")
            day_frame.columnconfigure(0, weight=1, uniform="a")

            # Displaying weather icons
            next_day_weather_icon_path = f"/Users/katia/Python Projects/Weather App/Weather_icons/{weather_codes[i]}.png"
            original_daily_weather_icon = Image.open(next_day_weather_icon_path).resize((70, 70), Image.Resampling.LANCZOS)
            daily_weather_icon_tk = ImageTk.PhotoImage(original_daily_weather_icon)
            daily_weather_icon_canvas = tk.Canvas(day_frame, background = "#219ebc", bd=0, highlightthickness=0, relief="ridge")
            daily_weather_icon_canvas.grid(column=0, row=0, sticky="nsew")
            daily_weather_icon_canvas.create_image(70, 44, anchor="center", image=daily_weather_icon_tk)
            day_frame.image = daily_weather_icon_tk

            # Displaying daily temperature / day of the week
            daily_info_label_weekday = tk.Label(day_frame, background = "#003049", text=str(next_days_of_the_week[i]), font=("Montserrat", 17), anchor="center", justify="center")
            daily_info_label_weekday.grid(row = 1, column = 0, sticky="sew")
            daily_info_label_temp = tk.Label(day_frame, background = "#003049", text=str(temperatures[i]) + " °C", font=("Montserrat", 19), fg="#f77f00", anchor="center", justify="center")
            daily_info_label_temp.grid(row = 2, column = 0, sticky="nsew")


if __name__ == "__main__":
    app = Weather_App()