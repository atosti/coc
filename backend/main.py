import http.client

import requests

# TIME_SERIES_INTRADAY API call
def intradayTimeSeries(symbol, interval, vaApiKey):
    resp = requests.get('https://www.alphavantage.co/query?'
    + 'function=TIME_SERIES_INTRADAY&symbol=' + symbol
    + '&interval=' + interval
    + '&apikey=' + vaApiKey)
    return resp

# Fetches your API key from the "avApi.txt" file
# This file should ONLY contain the API key, no other text/linebreaks
f = open('./backend/avApi.txt', "r")
lines = list(f)
vaApiKey = ''.join(lines)

# intradayTimeSeries('MSFT', '5min', vaApiKey)

# Make a GET request
resp = intradayTimeSeries('IP', '5min', vaApiKey)
print('VA Response: ' + resp.text)
