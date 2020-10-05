import requests, json, webbrowser, alg, excel
from bs4 import BeautifulSoup

def fetchMktCap(symbol):
    mktCap = None
    url = 'https://finance.yahoo.com/quote/' + symbol.lower()
    page = requests.get(url)
    soup = BeautifulSoup(page.content, 'html.parser')
    findMktCap = soup.find("td", {"data-test": "MARKET_CAP-value"})
    if findMktCap:
        mktCap = findMktCap.get_text(strip=True)
        # Convert from Trillions/Billions/Millions to raw int
        if "T" in mktCap:
            mktCap = float(mktCap[:-1]) * 1000000000000
        elif "B" in mktCap:
            mktCap = float(mktCap[:-1]) * 1000000000
        elif "M" in mktCap:
            mktCap = float(mktCap[:-1]) * 1000000
    return mktCap
# Book value per share (mrq)
def fetchBvps(symbol):
    bvps = None
    url = 'https://finance.yahoo.com/quote/' + symbol.upper() + '/key-statistics'
    page = requests.get(url)
    soup = BeautifulSoup(page.content, 'html.parser')
    # findBvps = soup.find("td", {"data-reactid": "599"})
    findBvps = soup.find(text='Book Value Per Share')
    if findBvps:
        fetch = findBvps.parent.parent.parent.findChildren()
        # TODO - Currently just grabs the 4th element. Find a better way.
        elem = fetch[3]
        bvps = float(elem.get_text(strip=True))
    return bvps

def fetchFinancials(symbol):
    financialsDict = {"eps": None, "epsList": None, "sales": None}
    url = 'https://www.marketwatch.com/investing/stock/' + symbol.lower() + '/financials'
    page = requests.get(url)
    soup = BeautifulSoup(page.content, 'html.parser')
    # Earnings Per Share (EPS)
    findEps = soup.find("a", {"data-ref": "ratio_Eps1YrAnnualGrowth"})
    if findEps:
        fetch = findEps.parent.parent.findChildren()
        for elem in fetch:
            curr = elem.find("div", {"class": "miniGraph"})
            if curr:
                # Elements are ordered from 2015 -> 2019
                values = json.loads(curr.get("data-chart"))["chartValues"]
                epsList = values
                eps = float(values[-1])
                financialsDict.update(eps = eps, epsList = epsList)
    # Revenue
    findSales = soup.find("a", {"data-ref": "ratio_SalesNet1YrGrowth"})
    if findSales:
        fetch = findSales.parent.parent.findChildren()
        for elem in fetch:
            curr = elem.find("div", {"class": "miniGraph"})
            if curr:
                values = json.loads(curr.get("data-chart"))["chartValues"]
                sales = None
                if values[-1] is not None:
                    sales = float(values[-1])
                financialsDict.update(sales = sales)
    return financialsDict

def fetchBalanceSheet(symbol):
    balanceSheetDict = {"price": None, "assets": None, "liabilities": None}
    url = 'https://www.marketwatch.com/investing/stock/' + symbol.lower() + '/financials/balance-sheet'
    page = requests.get(url)
    soup = BeautifulSoup(page.content, 'html.parser')
    # Price
    findPrice = soup.find("div", {"class": "lastprice"})
    if findPrice:
        fetch = findPrice.findChildren()
        for elem in fetch:
            curr = elem.find("p", {"class": "data bgLast"})
            if curr:
                price = float(curr.get_text(strip=True))
                balanceSheetDict.update(price = price)
    # Total Assets of last 5 years
    findAssets = soup.find("tr", {"class": "totalRow"})
    if findAssets:
        fetch = findAssets.findChildren()
        for elem in fetch:
            curr = elem.find("div", {"class": "miniGraph"})
            if curr:
                values = json.loads(curr.get("data-chart"))["chartValues"]
                assets = int(values[-1])
                balanceSheetDict.update(assets = assets)
    # Liabilities
    findLiabilites = soup.find("a", {"data-ref": "ratio_TotalLiabilitiesToTotalAssets"})
    if findLiabilites:
        fetch = findLiabilites.parent.parent.findChildren()
        for elem in fetch:
            curr = elem.find("div", {"class": "miniGraph"})
            if curr:
                values = json.loads(curr.get("data-chart"))["chartValues"]
                liabilities = int(values[-1])
                balanceSheetDict.update(liabilities = liabilities)
    return balanceSheetDict

def fetchProfile(symbol):
    profileDict = {"currRatio": None, "peRatio": None, "pbRatio": None}
    # Current Ratio
    url = 'https://www.marketwatch.com/investing/stock/' + symbol.lower() + '/profile'
    page = requests.get(url)
    soup = BeautifulSoup(page.content, 'html.parser')
    findCurrRatio = soup.find(text='Current Ratio')
    if findCurrRatio:
        fetch = findCurrRatio.parent.parent
        currRatio = float(fetch.find("p", {"class": "lastcolumn"}).get_text(strip=True))
        profileDict.update(currRatio = currRatio)
    # P/E Ratio
    findPeRatio = soup.find(text='P/E Current')
    if findPeRatio:
        fetch = findPeRatio.parent.parent
        peRatio = float(fetch.find("p", {"class": "lastcolumn"}).get_text(strip=True))
        profileDict.update(peRatio = peRatio)
    # P/B Ratio
    findPbRatio = soup.find(text='Price to Book Ratio')
    if findPbRatio:
        fetch = findPbRatio.parent.parent
        pbRatio = float(fetch.find("p", {"class": "lastcolumn"}).get_text(strip=True))
        profileDict.update(pbRatio = pbRatio)
    return profileDict

# TODO - SeekingAlpha triggers a captcha. Either solve it or find a new site.
def fetchDividends(symbol):
    dividendsList = {"years": [], "avgDividend": []}
    url = 'https://seekingalpha.com/symbol/' + symbol.upper() + '/dividends/history'
    page = requests.get(url)
    soup = BeautifulSoup(page.content, 'html.parser')
    findDividends = soup.find("div", {"id": "history-container"})
    return dividendsList

def scrape(symbol):
    #Initialize criteria
    price = sales = mktCap = eps = peRatio = pbRatio = currRatio = None
    grahamNum = assets = liabilities = epsList = dividends = None
    # Elements are ordered from 2015 -> 2019
    epsList = dividendList = []
    # Yahoo Finance Quote
    mktCap = fetchMktCap(symbol)
    # Yahoo Finance Key Stats
    bvps = fetchBvps(symbol)
    # MarketWatch Financials
    financialsDict = fetchFinancials(symbol)
    eps = financialsDict["eps"]
    epsList = financialsDict["epsList"]
    sales = financialsDict["sales"]
    # MarketWatch Balance Sheet
    balanceSheetDict = fetchBalanceSheet(symbol)
    price = balanceSheetDict["price"]
    assets = balanceSheetDict["assets"]
    liabilities = balanceSheetDict["liabilities"]
    # MarketWatch Profile
    profileDict = fetchProfile(symbol)
    currRatio = profileDict["currRatio"]
    peRatio = profileDict["peRatio"]
    pbRatio = profileDict["pbRatio"]
    # Seeking Alpha Dividends
    dividendsList = fetchDividends(symbol)

    # TODO - Fetch the following, final criteria:
    # Get last 20 years of dividend history. If they have a dividend, check whether they've had consistent payments.
    # Determine if they ever missed a payment or paid a decreasing dividend
    # url = 'https://www.marketwatch.com/investing/stock/' + symbol.lower() + '/financials/cash-flow'
    # dividendList
    # TODO = Print this data to an excel document. Update each symbol per fetch
    # excel.update(symbol, None)

    score = alg.score(mktCap, sales, peRatio, currRatio, epsList, dividends, assets, liabilities)
    print("Score: " + str(score) + "/7")
    grahamNum = None
    if bvps is not None and eps is not None:
        grahamNum = alg.grahamNum(eps, bvps)
        if grahamNum is not None:
            grahamNum = round(grahamNum, 2)
    print("Graham Num|Price: " + str(grahamNum) + "|" + str(price))
    return

def commands(phrase):
    args = phrase.split(' ')
    symbol = str(args[0])
    scrape(symbol)
    return