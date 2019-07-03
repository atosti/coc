import http.client

# FIXME - Move this functionality to a helper method/file later
vaApi = 'https://www.alphavantage.co/query?function=TIME_SERIES_INTRADAY&symbol=MSFT&interval=5min&apikey=demo'

conn = http.client.HTTPSConnection('localhost', 8080)
h1 = http.client.HTTPConnection('www.python.org')
# h1
print('h1 connection established')