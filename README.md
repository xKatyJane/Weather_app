# Weather App

This weather app has been built in Python with TK Inter and it is based on data received from the tomorrow.io API.

## Resources

The Requests library is needed in order to send and receive API requests.

```bash
pip install requests
```

## Usage

To use the app you need to obtain a free API key from tomorrow.io. You can register here:
https://app.tomorrow.io/signin

You can save your credentials into a JSON file in this format:

{
    "apikey" : "......................."
}

Replace my JSON file with yours in line 60 of the main.py file.

Once the file is replaced, you can run the main.py script that will open the app.
