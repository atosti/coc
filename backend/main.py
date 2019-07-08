import http.client

# Fetch your API key from the "avApi.txt" file
# This file should ONLY contain the API key, and no other text
f = open('./backend/avApi.txt', "r")
lines = list(f)
vaApiKey = ''.join(lines)
print('Loaded API Key: ' + vaApiKey)

# FIXME - Move this functionality to a helper method/file later
# avApi = 'https://www.alphavantage.co/query?function=TIME_SERIES_INTRADAY&symbol=MSFT&interval=5min&apikey=demo'

# conn = http.client.HTTPSConnection('localhost', 8080)
# h1 = http.client.HTTPConnection('www.python.org')
# # h1
# print('h1 connection established')