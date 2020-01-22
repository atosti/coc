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

# Holds all data returned from a US Fundamentals call
class UF:
    assets = 0
    earnings = 0
    liabilities = 0
    shares = 0

    def fetch(self, cik):
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
                if ind == 'AssetsCurrent':
                    self.assets = float(row.split(',')[-1])
                elif ind == 'LiabilitiesCurrent':
                    self.liabilities = float(row.split(',')[-1])
                elif ind == 'NetIncomeLoss':
                    self.earnings = float(row.split(',')[-1])
                elif ind == 'WeightedAverageNumberOfDilutedSharesOutstanding':
                    self.shares = float(row.split(',')[-1])
        return

# Creates a CSV for storing ticker output
def createCsv():
    with open('output.csv', 'w', newline='') as csvfile:
        fieldnames = [
            'Symbol',
            'Criteria_of_7',
            'Market_Cap_over_$700M?',
            'P/E_below_15?',
            'Curr_Ratio_over_2?',
            'No_earnings_deficit_(10yrs)?',
            'No_missed_dividends_(20yrs)?',
            'EPS_avg_over_33%_(10yrs)?',
            "Cheap_assets?"
        ]
        writer = csv.DictWriter(csvfile, fieldnames = fieldnames)
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

def hasHealthyEarnings(earnings10yrs):
    # Check for enough years of data
    if len(earnings10yrs) < 10:
        return False
    for earnings in earnings10yrs:
        if earnings < 0:
            return False
    return True

def hasHealthyDividends(dividends20yrs):
    # Check for enough years of data
    if len(dividends20yrs) < 20:
        return False
    # TODO - Need to check that its been increasing or constant each year
    # for dividend in dividends20yrs:
    #     if dividend
    return True

def hasHealthyEps(eps10yrs):
    # Check for enough years of data
    if len(eps10yrs) < 10:
        return False
    for eps in eps10yrs:
        if eps < 0:
            return False
    return True

def hasCheapAssets(assets, liabilities, marketCap):
    if marketCap >= ((assets - liabilities) * 1.5):
        return False
    return True

# Analyzes a symbol and writes it to the output csv
def check(symbol):
    # All of the 7 criteria
    healthyMarketCap = False
    healthyPeRatio = False
    healthyCurrRatio = False
    healthyEarnings = False
    healthyDividends = False
    healthyEps = False
    cheapAssets = False
    # All the values required for determining health
    cik = fetchCik(symbol)
    uf = UF()
    uf.fetch(cik)
    price = sharePrice(symbol)
    marketCap = price * float(uf.shares)
    eps = float(uf.earnings / uf.shares)
    peRatio = float(price / eps)
    currRatio = float(uf.assets / uf.liabilities)
    # TODO - Fetch arrays of 10yr earnings, dividends, eps

    # Calls to determine health
    if hasHealthyMarketCap(marketCap):
        healthyMarketCap = True
    if hasHealthyPeRatio(peRatio):
        healthyPeRatio = True
    if hasHealthyCurrRatio(currRatio):
        healthyCurrRatio = True
    # if hasHealthyEarnings(earnings10yrs):
    #     healthyEarnings = True
    # if hasHealthyDividends(dividends20yrs):
    #     healthyDividends = True
    # if hasHealthyEps(eps10yrs):
    #     healthyEps = True
    if hasCheapAssets(uf.assets, uf.liabilities, marketCap):
        cheapAssets = True

    # TODO - Call a method for modifying the csv
    #   1) First just add a new line with the proper data
    #   2) Then change it to search for a symbol and write that row

    return