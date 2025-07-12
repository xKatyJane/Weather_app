# Weather App

This weather app has been built in Python with Tkinter and it is based on data received from the tomorrow.io API.

## Resources

The Requests library is needed in order to send and receive API requests.

```bash
pip install requests
```

## Usage

To use the app you need to obtain a free API key from tomorrow.io. You can register here:
https://app.tomorrow.io/signin

You can save your credentials into a JSON file in this format:

<code style="color : #00acc1">{ "apikey" : "......................." }</code>

Replace the path to the JSON file with credentials in line 60 of the main.py file.

Once the file is replaced, you can run the main.py script and that will open the app.

## Screenshots

<h4 align="center">The interface on opening.</h4>
<p align="center">
  <img src="https://raw.githubusercontent.com/xKatyJane/Weather_app/main/Screenshots/Main_menu.png" width="650">
</p>

<h4 align="center">The search results.</h4>
<p align="center">
  <img src="https://raw.githubusercontent.com/xKatyJane/Weather_app/main/Screenshots/Search_result_1.png" width="650">
</p>

<p align="center">
  <img src="https://raw.githubusercontent.com/xKatyJane/Weather_app/main/Screenshots/Search_result_2.png" width="650">
</p>

## Python packages used

- **API requests**: Requests
- **Interface**: Tkinter
- **Image management**: PIL
- **Date, time, timezone**: Datetime, Pytz, Timezone Finder

## Tomorrow.io data usage

The app uses icons and weather descriptions provided by the tomorrow.io. They can be found here:
https://docs.tomorrow.io/reference/data-layers-weather-codes
Powered by Tomorrow.io.
