import http.client

# Takes the Stock symbol to fetch and the time interval
def intradayTimeSeries(symbol, interval, vaApiKey):
    # https://www.alphavantage.co/query?function=TIME_SERIES_INTRADAY&symbol=MSFT&interval=5min&apikey=demo
    avUrl = 'www.alphavantage.co'

    # avUrl = 'www.alphavantage.co/query?function=TIME_SERIES_INTRADAY&symbol='
    # avUrl += symbol + '&interval=' + interval + '&apikey=' + vaApiKey
    # # FIXME - Remove later
    # print('Url: ' + avUrl)

    conn = http.client.HTTPSConnection(avUrl, 443, timeout=10)
    conn.request("GET", "/")
    response = conn.getresponse()
    respBody = response.read()
    print(respBody)
    conn.close() #Close the connection when done
    return

# Fetches your API key from the "avApi.txt" file
# This file should ONLY contain the API key, no other text/linebreaks
f = open('./backend/avApi.txt', "r")
lines = list(f)
vaApiKey = ''.join(lines)

intradayTimeSeries('MSFT', '5min', vaApiKey)