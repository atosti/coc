import http.client, requests, json, csv, quandl, os
from datetime import date

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

# Checks the 7 criteria for a single symbol, and writes it to a csv
#   - Check the csv first for the symbol, if it already exists, skip all calls and just print the csv data.
#       Else, call AV and USF and determine the values
#   - Will be unable to easily update a csv. Instead have to create a new csv and rename it to change a single row.
def check(symbol, ufApiKey, avApiKey):
    # If file doesn't exist, create it
    if os.path.isfile('output.csv') == False:
        with open('output.csv', 'w', newline='') as csvfile:
            fieldnames = [
                'CIK',
                'Symbol',
                'Earnings_Per_Share(EPS)',
                'Current_Ratio',
                'Earnings',
                'Profits_to_Earnings_Ratio(PE)',
                'Earnings_Growth_Avg',
                'Large_Company?',
                'Conservatively_Financed?',
                'No_Missed_Dividends?',
                'No_Earnings_Deficit?',
                'Consistent_Earnings_Growth?',
                'Cheap_Assets?',
                'Cheap_Earnings?'
            ]
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
    else:
        # Read the output and check for the symbol
        with open('output.csv', 'r+', newline='') as csvfile:
            reader = csv.reader(csvfile)
            for row in reader:
                # Hardcodes to 2nd header
                currSym = str(row).split(';')[1]
                if(symbol == currSym):
                    # TODO - Output all the 7 pieces here, with line num? Maybe just nicely in console.
                    print('Already exists: ' + str(row))

    # TODO - Calculate the 7 datapoints and write them to the csv
    
    return

# FIXME - Delete this later.
# TODO - Currently hardcodes to CIK "1418091" (Twitter) for testing purposes.
#        Eventually, pass in the list of CIKs and run it on them all.
#      - Check the figures being passed for a company match its official financial reports
#      - Add status code check for AV API, also make the AV and USF calls not nested if possible
#      - Move USF indicator API call to its own method
#      - Some of my fundamentals values are based on TODAY, whereas others are EoY numbers. Make them consistent (e.g. Outstanding shares)
#      - Check that the USFund API works on all my CIK Ids, as they're not all from the same exchange
#        I might need to take Exchange into consideration
def analyze(ufApiKey, avApiKey, quandlApiKey):
    # CSV File Creation/Setup
    with open('output.csv', 'w', newline='') as csvfile:
        # All criteria fields (Y/N) are listed last and contain a '?'
        fieldnames = [
            'CIK',
            'Symbol',
            'Earnings_Per_Share(EPS)',
            'Current_Ratio',
            'Earnings',
            'Profits_to_Earnings_Ratio(PE)',
            'Earnings_Growth_Avg',
            'Large_Company?',
            'Conservatively_Financed?',
            'No_Missed_Dividends?',
            'No_Earnings_Deficit?',
            'Consistent_Earnings_Growth?',
            'Cheap_Assets?',
            'Cheap_Earnings?'
        ]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

        # Reads the tickerInfo file and fetches all the CIK Ids and ticker symbols
        tickerList = list()
        cikList = list()
        with open('./backend/tickerInfo.txt', 'r') as tickerInfo:
            lines = list(tickerInfo)
            for line in lines:
                cikId = line.split('|')[0]
                ticker = line.split('|')[1]
                # Skips the first line, as it contains column headers
                if(cikId != 'CIK'):
                    cikList.append(cikId)
                    tickerList.append(ticker)
        # Loop through all CIK/Symbol pairs
        for company in range(len(tickerList)):
            symbol = tickerList[company]
            cik = cikList[company]
            # Call the US Fundamentals API
            usfResp = requests.get('https://api.usfundamentals.com/v1/indicators/xbrl?'
                + 'indicators=WeightedAverageNumberOfDilutedSharesOutstanding,'
                + 'AssetsCurrent,'
                + 'LiabilitiesCurrent,'
                + 'NetIncomeLoss'
                + '&companies=' + cik
                + '&token=' + ufApiKey)
            if usfResp.status_code == 200:
                indicators = usfResp.text
                print('USFund Resp: ' + '\n' + indicators) # FIXME - Remove later, for testing only.
                # Only analyze if all indicators are returned
                # FIXME - Handle if only SOME indicators are returned for a ticker
                # print("Length of ind lines: " + str(len(indicators.splitlines()))) # FIXME - Remove later, for testing only.
                if(len(indicators.splitlines()) == 5):
                    for line in indicators.splitlines():
                        ind = str(line).split(',')[1]
                        if ind == 'AssetsCurrent':
                            currAssets = float(line.split(',')[-1])
                            print('Current Assets: ' + str(currAssets))
                        elif ind == 'LiabilitiesCurrent':
                            currLiabilities = float(line.split(',')[-1])
                            print('Current Liabilities: ' + str(currLiabilities))
                        elif ind == 'NetIncomeLoss':
                            earnings = float(line.split(',')[-1]) # Gets current year
                            print('Earnings: ' + str(earnings)) # FIXME - Remove later, for testing.
                            # List of annual earnings numbers, removes CIK and Metric items
                            earningsDataList = line.split(',')
                            earningsDataList.pop(1)
                            earningsDataList.pop(0)
                            # Remove empty entries
                            while '' in earningsDataList:
                                earningsDataList.remove('')                                
                            print('Earnings Data List: ' + str(earningsDataList)) # FIXME - Remove later, for testing.
                            # Determines if 10 years of earnings data exists
                            tenYearEarningsAvailable = False
                            # Holds the avg of the last 10(or less) available years of EG
                            earningsGrowthAvg = float(0)
                            # Requires 11 values to determine last 10 years of growth
                            if(len(earningsDataList) > 11):
                                tenYearEarningsAvailable = True
                            if(tenYearEarningsAvailable):
                                earningsGrowthAvg = abs(float(earningsDataList[-10]) - float(earningsDataList[-1])) / float(earningsDataList[-10]) * 100
                            # Check that earningsDataList isn't fetched OOB
                            elif(len(earningsDataList) > 1):
                                earliestIndex = -1 * len(earningsDataList)
                                earningsGrowthAvg = abs(float(earningsDataList[earliestIndex]) - float(earningsDataList[-1])) / float(earningsDataList[earliestIndex]) * 100
                                # Handles the negative if switching between loss and profit
                                if(int(earningsDataList[earliestIndex]) < 0):
                                    earningsGrowthAvg *= -1
                            print('EG Avg: ' + str(earningsGrowthAvg)) # FIXME - For testing only.
                        elif ind == 'WeightedAverageNumberOfDilutedSharesOutstanding':
                            totalShares = float(line.split(',')[-1])
                            print('Total Shares: ' + str(totalShares))
                        else:
                            if ind != 'indicator_id':
                                print('Error - Unknown indicator: ' + ind)

                    #FIXME - Totally swap from AV API calls to Quandl for EoY price.
                    #      - Pass in the Stock symbol properly
                    #      - Fetch an appropriate amount of rows

                    # Quandl API Calls
                    qData = quandl.get(
                        'WIKI/TWTR',
                        start_date='2017-12-31',
                        end_date='2018-12-31',
                        collapse='annual',
                        column_index=1,
                        rows=1)
                    print('QDATA: ' + str(qData))
                    print('QD @ -1: ' + qData[0])

                    # AV API Calls
                    # TODO - See if the current price is needed, for now just use EoY values for consistency
                    #      - Could be beneficial in determining a recent Cheap Assets Ratio
                    # FIXME - Generate a string of today's date to pass to this, as it's currently hardcoded to a date
                    # currPrice = float(tsdJson['Time Series (Daily)']['2019-09-30']['4. close'])
                    # print('Current Price: ' + str(currPrice)) # FIXME - Remove later

                    # FIXME - Currently hardcoded to Twitter's symbol, fetch this from a dict based on each CIK later
                    avResponse = timeSeriesDaily(symbol, avApiKey)
                    tsdJson = json.loads(avResponse.text)
                    print('AV API Response: ' + '\n' + avResponse.text)
                    eoyPrice = float(tsdJson['Time Series (Daily)']['2018-12-31']['4. close']) # End of year price  

                    # Calculations
                    earningsPerShare = float(earnings) / float(totalShares)
                    currRatio = currAssets / currLiabilities
                    marketCap = eoyPrice * float(totalShares)
                    priceToEarningsRatio = eoyPrice / float(earningsPerShare)
                    # Criteria (Y/N)
                    # Keep them phrased where Y = Good, N = Bad
                    largeCompany = 'N'
                    conservativelyFinanced = 'N'
                    noMissedDividends = 'N'
                    noEarningsDeficit = 'N'
                    consistentEarningsGrowth = 'N'
                    cheapAssets = 'N'
                    cheapEarnings = 'N'
                    # Large Company (Sales > 700M)
                    if(earnings >= 700000000):
                        largeCompany = 'Y'
                    # Conservatively Financed (Curr Ratio > 200%)
                    if(currRatio >= 2.0):
                        conservativelyFinanced = 'Y'
                    # No Missed Dividends (in the last 10 yrs)
                    # TODO - What API can I get this from?
                    #      - For now could generate a link to a dividend site for this, for easier access
                    noMissedDividends = 'Unk.'
                    # No Earnings Deficit (in the last 10 yrs)
                    if(tenYearEarningsAvailable):
                        noEarningsDeficit = 'Y'
                        for i in range(-10, -1):
                            if(earningsDataList[i] < 0):
                                noEarningsDeficit = 'N'
                    # Consistent Earnings Growth (At least 33% earnings growth over the last 10 yrs. So, 2.9% annually for last 10 yrs)
                    if(tenYearEarningsAvailable and (earningsGrowthAvg > 33.0)):
                        consistentEarningsGrowth = 'Y'
                    # Cheap Assets (Market cap < (Assets - Liabilites) * 1.5 )
                    if(marketCap < ((currAssets - currLiabilities) * 1.5)):
                        cheapAssets = 'Y'
                    # Cheap Earnings (P/E ratio < 15)
                    if(priceToEarningsRatio < 15):
                        cheapEarnings = 'Y'
                    
                    # Write the row
                    # FIXME - Color code the cells based on if a stock passes its criteria
                    # FIXME - Add a column for the annual price chart, that generates a Morningstar link for easy access
                    # FIXME - Fetch the CIK and Symbol dynamically
                    writer.writerow({
                        'CIK': cik,
                        'Symbol': symbol,
                        'Earnings_Per_Share(EPS)': str(earningsPerShare),
                        'Current_Ratio': str(currRatio),
                        'Earnings': str(earnings),
                        'Profits_to_Earnings_Ratio(PE)': str(priceToEarningsRatio),
                        'Earnings_Growth_Avg': str(earningsGrowthAvg),
                        'Large_Company?': largeCompany,
                        'Conservatively_Financed?': conservativelyFinanced,
                        'No_Missed_Dividends?': noMissedDividends,
                        'No_Earnings_Deficit?': noEarningsDeficit,
                        'Consistent_Earnings_Growth?': consistentEarningsGrowth,
                        'Cheap_Assets?': cheapAssets,
                        'Cheap_Earnings?': cheapEarnings
                    })
    return

# Command processing
def commands(phrase, avApiKey, ufApiKey, quandlApiKey):
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
    # Disabled, as it makes too many calls to be useful.
    # elif cmd == 'analyze' or cmd == 'analyse':
    #     analyze(ufApiKey, avApiKey, quandlApiKey)
    elif cmd == 'check':
        if len(keywords) < 2:
            print('Invalid syntax. Check requires a symbol.')
        else:
            check(keywords[1], ufApiKey, avApiKey)
    elif cmd == 'quit' or cmd == 'exit':
        print('Exiting...')
    else:
        print('Unrecognized command: ' + cmd)
    return
