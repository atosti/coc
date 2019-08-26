import http.client

import requests

# TIME_SERIES_INTRADAY API call
def timeSeriesDaily(symbol, interval, avApiKey):
    resp = requests.get('https://www.alphavantage.co/query?'
    + 'function=TIME_SERIES_INTRADAY&symbol=' + symbol
    + '&interval=' + interval
    + '&apikey=' + avApiKey)
    return resp

# TIME_SERIES_DAILY_ADJUSTED API call
def timeSeriesDailyAdjusted(symbol, avApiKey):
    resp = requests.get('https://www.alphavantage.co/query?'
    + 'function=TIME_SERIES_DAILY_ADJUSTED&symbol=' + symbol
    + '&apikey=' + avApiKey)
    return resp

# Command processing
def commandHandler(phrase):
    keywords = phrase.split(' ')
    cmd = keywords[0] # Gets the command keyword

    if cmd == 'help':
        print('TBD - List of usable commands here!')
    elif cmd == 'tsd':
        if len(keywords) < 3:
            print('Invalid syntax. Time Series Daily requires a symbol'
            + ' and interval to be passed.')
        else:
            print('Response: '
            + timeSeriesDaily(keywords[1], keywords[2], avApiKey).text)
    elif cmd == 'tsda':
        if len(keywords) < 2:
            print('Invalid syntax. Time Series Daily Adjusted requires a symbol'
            + ' to be passed.')
        else:
            print('Response: '
            + timeSeriesDailyAdjusted(keywords[1], avApiKey).text)
    elif cmd == 'quit' or cmd == 'exit':
        print('Exiting...')
    else:
        print('Unrecognized command: ' + cmd)
    return

# Fetches your API key from the "avApiKey.txt" file
f = open('./backend/avApiKey.txt', "r")
lines = list(f)
avApiKey = ''.join(lines)

# Command loop
phrase = ''
print('Enter a command(type \'quit\' or \'exit\' when finished):')
while (phrase != 'quit' and phrase != 'exit'):
    print('$ ', end='') # Signals to the user they're in a command prompt
    phrase = input()
    phrase = phrase.lower()
    commandHandler(phrase)


# Make a GET request for testing
# resp = timeSeriesDaily('MSFT', '5min', avApiKey)
# print('VA Response: ' + resp.text)

# resp2 = timeSeriesDailyAdjusted('IP', avApiKey)
# print('tsDailyAdjusted: ' + resp2.text)

# TODO - Figure out Annual earnings (historical if possible)
