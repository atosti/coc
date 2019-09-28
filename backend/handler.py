import http.client
import requests
import json

# FIXME - Add HTTP status code checking for the AV API calls
# FIXME - Add proper error handling for these methods

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

# Fetches/Creates a list of CIK IDs for all US Companies
def getCikIds(ufApiKey):
    resp = requests.get('https://api.usfundamentals.com/v1/companies/xbrl?'
    + 'format=json'
    + '&token=' + ufApiKey)
    if resp.status_code == 200:
        f = open("./backend/ciks.txt","w")
        # FIXME - Take this JSON Response, and filter it down to be just CIK IDs, then write that to the file.
        companies = json.loads(resp.text)
        for company in companies:
            f.write(company + "\n")
            # f.write(company["company_id"] + "\n")
        f.close()
    else:
        print('Error when reaching UF API')
        return
    return

# TODO - Analyze all of the following on each stock symbol
# 1. What are the earnings per share?
# 2. Are annual earnings over $700M? (Is it a large company?)
# 3. Is it conservatively financed? (Current ratio of 200%)
# 	* Current ratio = Current assets / current liabilities
# 4. Dividend history (Have they missed any dividends in the last 20 years?)
# 5. Have they had no earnings deficit in the last 10 years?
# 6. How is earnings growth? (At least 2.9% annually for 10 years)
# 7. Does it have Cheap Assets? (Market cap < (Assets - liabilities) * 1.5
# 	* A ratio less than 1 is good
# 8. Does it have Cheap earnings? (P/E ratio < 15)

def analyze(ufApiKey):
    return


# Command processing
def commands(phrase, avApiKey, ufApiKey):
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
    # Fetches the list of all CIK IDs a writes them to a local dictionary
    elif cmd == 'init':
        getCikIds(ufApiKey)
        print('CIK IDs successfully fetched from US Fundamentals')
    elif cmd == 'quit' or cmd == 'exit':
        print('Exiting...')
    else:
        print('Unrecognized command: ' + cmd)
    return
