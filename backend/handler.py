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

# Fetches/Creates a list of CIK Ids for all US Companies
def getCikIds(ufApiKey):
    resp = requests.get('https://api.usfundamentals.com/v1/companies/xbrl?'
    + 'format=json'
    + '&token=' + ufApiKey)
    if resp.status_code == 200:
        # Populates a list of CIK Ids
        f = open('./backend/ciks.txt','w')
        companies = json.loads(resp.text)
        for company in companies:
            f.write(company["company_id"] + "\n")
        f.close()
    else:
        print('Error when reaching UF API')
        return
    return

# TODO - Analyze all of the following on each stock symbol
# 1. What are the earnings per share?
# 4. Dividend history (Have they missed any dividends in the last 20 years?)
# 5. Have they had no earnings deficit in the last 10 years?
# 6. How is earnings growth? (At least 2.9% annually for 10 years)
# 7. Does it have Cheap Assets? (Market cap < (Assets - liabilities) * 1.5
# 	* A ratio less than 1 is good
# 8. Does it have Cheap earnings? (P/E ratio < 15)

# Notes:
# OperatingIncomeLoss = Earnings BEFORE taxes are deducted (but after operting expenses)
# Revenues = Income before expenses AND taxes are deducted (gross sales)
# So, therefore:
#   - OperatingIncomeLoss = Revenues - expenses
#   - Earnings = OperatingIncomeLoss - taxes
# NetIncome = Earnings (which is income after taxes/expenses)

# TODO - Currently hardcodes to CIK "1418091" (Twitter) for testing purposes.
#         Eventually, pass in the list of CIKs and run it on them all.
#      - Additionally, arrange this output into an EXCEL document
#      - Add proper handling for indicators that aren't returned
#      - Check the figures being passed for a company match its official financial reports
def analyze(ufApiKey, avApiKey):
    # https://api.usfundamentals.com/v1/indicators/xbrl?indicators=AssetsCurrent,LiabilitiesCurrent&companies=1418091&token=ZN6kXxgpXMxFUQGcUOkZGw

    # 2. Are annual earnings over $700M? (Is it a large company?)
    # 3. Is it conservatively financed? (Current ratio of 200%)
    # 	* Current ratio = Current assets / current liabilities
    resp = requests.get('https://api.usfundamentals.com/v1/indicators/xbrl?'
        + 'indicators=AssetsCurrent,LiabilitiesCurrent,NetIncomeLoss'
        + '&companies=' + '1418091'
        + '&token=' + ufApiKey)
    if resp.status_code == 200:
        # companies = json.loads(resp.text)
        indicators = resp.text
        print('USFund Resp: ' + indicators)
        # Current Ratio from most recent year
        indicator = indicators.split('\n')[1]
        currAssets = indicator.split(',')[-1] # Gets most recent year
        indicator = indicators.split('\n')[2]
        currLiabilities = indicator.split(',')[-1]
        currRatio = str(int(currAssets) / int(currLiabilities))
        print('Current Ratio: ' + currRatio) # FIXME - Remove later
        if(float(currRatio) > 2.0):
            print('Over 200% current ratio? ' + 'Y')
        else:
            print('Over 200% current ratio? ' + 'N')
        # Earnings from most recent year
        indicator = indicators.split('\n')[3]
        earnings = indicator.split(',')[-1]
        print('Earnings: ' + earnings) # FIXME - Remove later
        if(int(earnings) > 700000000):
            print('Over $700M/yr? ' + 'Y')
        else:
            print('Over $700M/yr? ' + 'N')
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
    # Fetches the list of all CIK Ids a writes them to a local dictionary
    elif cmd == 'init':
        getCikIds(ufApiKey)
        print('CIK Ids successfully fetched from US Fundamentals')
    elif cmd == 'analyze' or cmd == 'analyse':
        analyze(ufApiKey, avApiKey)
    elif cmd == 'quit' or cmd == 'exit':
        print('Exiting...')
    else:
        print('Unrecognized command: ' + cmd)
    return
