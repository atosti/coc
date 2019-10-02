import http.client
import requests
import json

# FIXME - Add HTTP status code checking for the AV API calls
# FIXME - Add proper error handling for these methods

# TIME_SERIES_INTRADAY API call
def timeSeriesDaily(symbol, avApiKey):
    resp = requests.get('https://www.alphavantage.co/query?'
    + 'function=TIME_SERIES_DAILY'
    + '&symbol=' + symbol
    + '&outputsize=full'
    + '&apikey=' + avApiKey)
    return resp

# TIME_SERIES_DAILY_ADJUSTED API call
def timeSeriesDailyAdjusted(symbol, avApiKey):
    resp = requests.get('https://www.alphavantage.co/query?'
    + 'function=TIME_SERIES_DAILY_ADJUSTED'
    + '&symbol=' + symbol
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
# 4. Dividend history (Have they missed any dividends in the last 20 years?)
# 5. Have they had no earnings deficit in the last 10 years?
#   - Need to handle if the stock is less than 10 years old (i.e. for TWTR)
# 6. How is earnings growth? (At least 2.9% annually for 10 years)
#   - Need to handle if the stock is less than 10 years old (i.e. for TWTR)

# TODO - Currently hardcodes to CIK "1418091" (Twitter) for testing purposes.
#        Eventually, pass in the list of CIKs and run it on them all.
#      - Additionally, arrange this output into an EXCEL document
#      - Add proper handling for indicators that aren't returned
#      - Check the figures being passed for a company match its official financial reports
#      - Add the stock symbols to the CIK dict, so they can be easily referenced
#      - Add status code check for AV API, also make the AV and USF calls not nested if possible
#      - Move USF indicator API call to its own method
#      - Some of my fundamentals values are based on TODAY, whereas others are EoY numbers. Make them consistent (e.g. Outstanding shares)

# Note: The USF response puts the indicators in alphabetical order. Change the indicator arrays to match appropriately when adding new params to a request
def analyze(ufApiKey, avApiKey):
    # https://api.usfundamentals.com/v1/indicators/xbrl?indicators=AssetsCurrent,LiabilitiesCurrent&companies=1418091&token=ZN6kXxgpXMxFUQGcUOkZGw

    # 1. What are the earnings per share?
    # 2. Are annual earnings over $700M? (Is it a large company?)
    # 3. Is it conservatively financed? (Current ratio of 200%)
    # 	* Current ratio = Current assets / current liabilities
    # 7. Does it have Cheap Assets? (Market cap < (Assets - liabilities) * 1.5
    # 	* A ratio less than 1 is good
    # 8. Does it have Cheap earnings? (P/E ratio < 15)
    usfResp = requests.get('https://api.usfundamentals.com/v1/indicators/xbrl?'
        + 'indicators=WeightedAverageNumberOfDilutedSharesOutstanding,'
        + 'AssetsCurrent,'
        + 'LiabilitiesCurrent,'
        + 'NetIncomeLoss'
        + '&companies=' + '1418091'
        + '&token=' + ufApiKey)
    if usfResp.status_code == 200:
        # US Fund API Calls
        indicators = usfResp.text
        print('USFund Resp: ' + indicators)
        for line in indicators.splitlines():
            ind = str(line).split(',')[1]
            if ind == 'AssetsCurrent':
                currAssets = float(line.split(',')[-1])
                print('Current Assets: ' + str(currAssets))
            elif ind == 'LiabilitiesCurrent':
                currLiabilities = float(line.split(',')[-1])
                print('Current Liabilities: ' + str(currLiabilities))
            elif ind == 'NetIncomeLoss':
                # FIXME - For all the returned results, create an earnings var for it. Need this to determine earnings growth.
                earnings = float(line.split(',')[-1])
                print('Earnings: ' + str(earnings))
            elif ind == 'WeightedAverageNumberOfDilutedSharesOutstanding':
                totalShares = float(line.split(',')[-1])
                print('Total Shares: ' + str(totalShares))
            else:
                print('Error - Unknown indicator fetched.')

        # AV API Calls
        # TODO - See if the current price is needed, for now just use EoY values for consistency
        #      - Could be beneficial in determining a recent Cheap Assets Ratio
        # FIXME - Generate a string of today's date to pass to this, as it's currently hardcoded to a date
        # currPrice = float(tsdJson['Time Series (Daily)']['2019-09-30']['4. close'])
        # print('Current Price: ' + str(currPrice)) # FIXME - Remove later

        # FIXME - Currently hardcoded to Twitter's symbol, fetch this from a dict based on each CIK later
        tsdJson = json.loads(timeSeriesDaily('TWTR', avApiKey).text)
        eoyPrice = float(tsdJson['Time Series (Daily)']['2018-12-31']['4. close']) # End of year price  
        # Calculations
        earningsPerShare = float(earnings) / float(totalShares)
        currRatio = currAssets / currLiabilities
        epsPercentage = 100 * (earningsPerShare / eoyPrice)
        marketCap = eoyPrice * float(totalShares)
        cheapAssetsRatio = marketCap / (float((currAssets - currLiabilities) * 1.5))
        priceToEarningsRatio = eoyPrice / float(earningsPerShare)
        
        # 1. Earnings per share from most recent year
        print('1. Earnings/Share (EPS): ' + str(earningsPerShare)) # FIXME - Remove later
        # 2. Current Ratio from most recent year
        if(currRatio > 2.0):
            print('2. Over 200% current ratio? ' + 'Y')
        else:
            print('2. Over 200% current ratio? ' + 'N')
        # 3. Earnings from most recent year
        if(earnings > 700000000):
            print('3. Over $700M/yr? ' + 'Y')
        else:
            print('3. Over $700M/yr? ' + 'N')
        # 7. Does it have Cheap Assets? (Market cap < (Assets - liabilities) * 1.5)
        if(marketCap < ((currAssets - currLiabilities) * 1.5)):
            print('7. Cheap assets? ' + 'Y')
        else:
            print('7. Cheap assets? ' + 'N')
        # 8. Does it have Cheap earnings? (P/E ratio < 15)
        print('P/E Ratio (< 15 is good): ' + str(priceToEarningsRatio)) # FIXME - Remove later
        if(priceToEarningsRatio < 15):
            print('8. Does it have cheap earnings? ' + 'Y')
        else:
            print('8. Does it have cheap earnings? ' + 'N')

        # Additional datapoints. Relevant for testing.
        print('End of Year Price: ' + str(eoyPrice)) # FIXME - Remove later
        print('Market Cap: ' + str(marketCap))
        print('Current Ratio: ' + str(currRatio)) # FIXME - Remove later
        print('EPS Percentage: ' + str(round(epsPercentage, 2)) + '%') # FIXME - Remove later
        print('Cheap Assets Ratio (< 1 is good): ' + str(cheapAssetsRatio)) # FIXME - Remove later

    return

# Command processing
def commands(phrase, avApiKey, ufApiKey):
    keywords = phrase.split(' ')
    cmd = keywords[0] # Gets the command keyword
    if cmd == 'help':
        print('TBD - List of usable commands here!')
    elif cmd == 'tsd':
        if len(keywords) < 2:
            print('Invalid syntax. Time Series Daily requires a symbol'
            + ' to be passed.')
        else:
            print('Response: '
            + timeSeriesDaily(keywords[1], avApiKey).text)
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
