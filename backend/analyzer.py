import csv, json, os.path, requests

# Fetch the API keys
f = open('./backend/keys/alpha-vantage.txt', 'r')
lines = list(f)
avKey = ''.join(lines)
f.close()

f = open('./backend/keys/us-fundamentals.txt', 'r')
lines = list(f)
ufKey = ''.join(lines)
f.close()

# Sets the end of year date (can be updated as years change)
eoyDateStr = '2018-12-31'
eoyDateYr = '2018'

# Holds all data returned from a US Fundamentals call
class UF:
    assets = []
    earnings = []
    liabilities = []
    shares = []
    years = []

    def fetch(self, cik):
        print('UF Call:\n' +
            'https://api.usfundamentals.com/v1/indicators/xbrl?' +
            'indicators=' +
            'AssetsCurrent,' +
            'LiabilitiesCurrent,' +
            'NetIncomeLoss,' +
            'WeightedAverageNumberOfDilutedSharesOutstanding' +
            '&companies=' + cik +
            '&token=' + ufKey
        ) # FIXME - Remove later
        ufResp = requests.get(
            'https://api.usfundamentals.com/v1/indicators/xbrl?' +
            'indicators=' +
            'AssetsCurrent,' +
            'LiabilitiesCurrent,' +
            'NetIncomeLoss,' +
            'WeightedAverageNumberOfDilutedSharesOutstanding' +
            '&companies=' + cik +
            '&token=' + ufKey
        )
        if(ufResp.status_code == 200):
            indicatorRows = ufResp.text
            for row in indicatorRows.splitlines():
                ind = str(row).split(',')[1]
                if ind == 'indicator_id':
                    for item in row.split(',')[2:]:
                        self.years.append(item)
                elif ind == 'AssetsCurrent':
                    for item in row.split(',')[2:]:
                        self.assets.append(float(item))
                elif ind == 'LiabilitiesCurrent':
                    for item in row.split(',')[2:]:
                        self.liabilities.append(float(item))
                elif ind == 'NetIncomeLoss':
                    for item in row.split(',')[2:]:
                        self.earnings.append(float(item))
                elif ind == 'WeightedAverageNumberOfDilutedSharesOutstanding':
                    for item in row.split(',')[2:]:
                        self.shares.append(float(item))
        return

# Holds all the data associated with an 'output.csv' row
class CsvRow:
    symbol = ''
    numCriteria = 0
    healthyMarketCap = False
    healthyPeRatio = False
    healthyCurrRatio = False
    healthyEarnings = False
    healthyDividends = False
    healthyEps = False
    healthyAssets = False

# Creates a CSV for storing ticker output
def createCsv():
    with open('output.csv', 'w', newline = '') as file:
        fieldnames = [
            'Symbol',
            'Criteria_of_7',
            'Market_Cap_over_$700M?',
            'P/E_below_15?',
            'Curr_Ratio_over_2?',
            'No_earnings_deficit_(10yrs)?',
            'No_missed_dividends_(20yrs)?',
            'EPS_avg_over_33%_(10yrs)?',
            'Cheap_assets?'
        ]
        writer = csv.DictWriter(file, fieldnames = fieldnames)
        writer.writeheader()
    return

# Create the output csv if necesary
if not os.path.isfile('./output.csv'):
    createCsv()

#Fetches CIK associated with the ticker symbol
def fetchCik(symbol):
    cik = ''
    with open('./backend/tickers.txt', 'r') as tickers:
        tickerRows = list(tickers)
        for row in tickerRows:
            cik = row.split('|')[0]
            currSymbol = row.split('|')[1].lower()
            if(symbol == currSymbol):
                return cik
    return cik

# Gets EoY share price
def sharePrice(symbol):
    response = requests.get(
        'https://www.alphavantage.co/query?'
        + 'function=TIME_SERIES_DAILY'
        + '&symbol=' + symbol
        + '&outputsize=full'
        + '&apikey=' + avKey
    )
    jsonResp = json.loads(response.text)
    price = float(jsonResp['Time Series (Daily)'][eoyDateStr]['4. close'])
    return price

def hasHealthyMarketCap(marketCap):
    if marketCap >= 700000000:
        return True
    return False

def hasHealthyPeRatio(peRatio):
    if peRatio <= 15:
        return True
    return False

def hasHealthyCurrRatio(currRatio):
    if currRatio >= 2.0:
        return True
    return False

# FIXME - Change to only consider the most recent 10 years of data
def hasHealthyEarnings(earnings10yrs):
    # Check for enough years of data
    if len(earnings10yrs) < 10:
        return False
    for earnings in earnings10yrs:
        if earnings < 0:
            return False
    return True

# FIXME - Untested as no API data available to test this
def hasHealthyDividends(dividends20yrs):
    # Check for enough years of data
    if len(dividends20yrs) < 20:
        return False
    # TODO - Need to check that its been increasing or constant each year
    return True

def hasHealthyEps(earnings, shares, years):
    # Determines if EPS has increased on avg. > 33% over last 10 yrs
    i = 0 # Index of the current Eoy Date
    for year in years:
        if year == eoyDateYr:
            return i
        i += 1
    eps = earnings[i]
    epsPrio = earnings[i - 10]
    diff = float(epsPrio / eps)
    print('Diff: ' + diff) # FIXME - Remove later
    if diff >= 33.0:
        return True
    return False

def hasHealthyAssets(assets, liabilities, marketCap):
    if marketCap >= ((assets - liabilities) * 1.5):
        return False
    return True

# Updates the csv with a new row
# TODO - Prevent Symbol dupes. Currently will simply append a new row.
def updateCsv(symbol, csvRow):
    fieldnames = [
            'Symbol',
            'Criteria_of_7',
            'Market_Cap_over_$700M?',
            'P/E_below_15?',
            'Curr_Ratio_over_2?',
            'No_earnings_deficit_(10yrs)?',
            'No_missed_dividends_(20yrs)?',
            'EPS_avg_over_33%_(10yrs)?',
            'Cheap_assets?'
        ]
    with open('output.csv', 'a', newline = '') as file:
        writer = csv.DictWriter(file, fieldnames = fieldnames)
        writer.writerow({
            'Symbol': csvRow.symbol,
            'Criteria_of_7': csvRow.numCriteria,
            'Market_Cap_over_$700M?': csvRow.healthyMarketCap,
            'P/E_below_15?': csvRow.healthyPeRatio,
            'Curr_Ratio_over_2?': csvRow.healthyCurrRatio,
            'No_earnings_deficit_(10yrs)?': csvRow.healthyEarnings,
            'No_missed_dividends_(20yrs)?': csvRow.healthyDividends,
            'EPS_avg_over_33%_(10yrs)?': csvRow.healthyEps,
            'Cheap_assets?': csvRow.healthyAssets
        })
    return

# Determines the number of critera matched
def numHealthyCriteria(csvRow):
    totalMatches = 0
    if csvRow.healthyMarketCap == True:
        totalMatches += 1
    if csvRow.healthyPeRatio == True:
        totalMatches += 1
    if csvRow.healthyCurrRatio == True:
        totalMatches += 1
    if csvRow.healthyEarnings == True:
        totalMatches += 1
    if csvRow.healthyDividends == True:
        totalMatches += 1
    if csvRow.healthyEps == True:
        totalMatches += 1
    if csvRow.healthyAssets == True:
        totalMatches += 1
    return totalMatches

# Analyzes a symbol and writes it to the output csv
def check(symbol):
    # Create/Initialize a row for CSV
    csvRow = CsvRow()
    csvRow.symbol = symbol.upper()
    csvRow.healthyMarketCap = False
    csvRow.healthyPeRatio = False
    csvRow.healthyCurrRatio = False
    csvRow.healthyEarnings = False
    csvRow.healthyDividends = False
    csvRow.healthyEps = False
    csvRow.healthyAssets = False
    csvRow.numCriteria = False
    # Fetch data from US Fundamentals call
    cik = fetchCik(symbol)
    uf = UF()
    uf.fetch(cik)

    # Calculate the values only if enough data is present
    if uf.years[-1] != eoyDateYr:
        # All values will be false. Data is unavailable.
        print('No UF data for ' + eoyDateYr)
    elif len(uf.years) < 10:
        # Healthy earnings, eps, and dividends cannot be calculated
        print('Less than 10 yrs of UF data available.')
        price = sharePrice(symbol)
        marketCap = float(price * uf.shares[-1])
        eps = float(uf.earnings[-1] / uf.shares[-1])
        peRatio = float(price / eps)
        currRatio = float(uf.assets[-1] / uf.liabilities[-1])

        csvRow.healthyMarketCap = hasHealthyMarketCap(marketCap)
        csvRow.healthyPeRatio = hasHealthyPeRatio(peRatio)
        csvRow.healthyCurrRatio = hasHealthyCurrRatio(currRatio)
        csvRow.healthyEarnings = False
        csvRow.healthyEps = False
        csvRow.healthyAssets = hasHealthyAssets(
            uf.assets[-1],
            uf.liabilities[-1],
            marketCap
        )
        # FIXME - No API known to fetch dividends. Set to False for now.
        csvRow.healthyDividends = False
    else:
        # Enough UF data is available to calculate all 7 criteria.
        price = sharePrice(symbol)
        marketCap = float(price * uf.shares[-1])
        eps = float(uf.earnings[-1] / uf.shares[-1])
        peRatio = float(price / eps)
        currRatio = float(uf.assets[-1] / uf.liabilities[-1])

        csvRow.healthyMarketCap = hasHealthyMarketCap(marketCap)
        csvRow.healthyPeRatio = hasHealthyPeRatio(peRatio)
        csvRow.healthyCurrRatio = hasHealthyCurrRatio(currRatio)
        csvRow.healthyEarnings = hasHealthyEarnings(uf.earnings)
        csvRow.healthyEps = hasHealthyEps(uf.earnings, uf.shares, uf.years)
        csvRow.healthyAssets = hasHealthyAssets(
            uf.assets[-1],
            uf.liabilities[-1],
            marketCap
        )
        # FIXME - No API known to fetch dividends. Set to False for now.
        csvRow.healthyDividends = False
    # Calculates the num criteria based on csvRow object
    csvRow.numCriteria = numHealthyCriteria(csvRow)
    # Write the CSV Row to the output csv
    updateCsv(symbol, csvRow)
    return