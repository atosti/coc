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

def mwFinancialsSearch(soup, text):
    itemDict = {"item": None, "itemList": None}
    found = soup.find("a", {"data-ref": text})
    if found:
        fetch = found.parent.parent.findChildren()
        for elem in fetch:
            elemFound = elem.find("div", {"class": "miniGraph"})
            if elemFound:
                values = json.loads(elemFound.get("data-chart"))["chartValues"]
                itemList = values
                item = float(values[-1])
                itemDict.update(itemList = itemList, item = item)
    return itemDict

def fetchFinancials(symbol):
    financialsDict = {"eps": None, "epsList": None, "sales": None, "salesList": None}
    url = 'https://www.marketwatch.com/investing/stock/' + symbol.lower() + '/financials'
    page = requests.get(url)
    soup = BeautifulSoup(page.content, 'html.parser')
    itemDict = mwFinancialsSearch(soup, "ratio_Eps1YrAnnualGrowth")
    financialsDict.update(eps = itemDict["item"])
    financialsDict.update(epsList = itemDict["itemList"])
    itemDict = mwFinancialsSearch(soup, "ratio_SalesNet1YrGrowth")
    financialsDict.update(sales = itemDict["item"])
    financialsDict.update(salesList = itemDict["itemList"])
    # print("Financials: " + str(financialsDict))
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
    # Total Assets
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
    # print("Balance Sheet: " + str(balanceSheetDict))
    return balanceSheetDict

# Marketwatch Company Profile scraper
def mwProfileSearch(soup, text):
    item = None
    found = soup.find(text=text)
    if found:
        fetch = found.parent.parent.find("td", {"class": "w25"})
        if fetch:
            value = fetch.get_text(strip=True)
            if value != "N/A":
                item = float(value)
    return item

def fetchProfile(symbol):
    profileDict = {"currRatio": None, "peRatio": None, "pbRatio": None}
    url = 'https://www.marketwatch.com/investing/stock/' + symbol.lower() + '/profile'
    page = requests.get(url)
    soup = BeautifulSoup(page.content, 'html.parser')
    profileDict.update(currRatio = mwProfileSearch(soup, "Current Ratio"))
    profileDict.update(peRatio = mwProfileSearch(soup, "P/E Current"))
    profileDict.update(pbRatio = mwProfileSearch(soup, "Price to Book Ratio"))
    # print("Profile: " + str(profileDict))
    return profileDict


# TODO - SeekingAlpha triggers a captcha. Either solve it or find a new site.
# def fetchDividends(symbol):
#     dividendsList = {"years": [], "avgDividend": []}
#     url = 'https://seekingalpha.com/symbol/' + symbol.upper() + '/dividends/history'
#     page = requests.get(url)
#     soup = BeautifulSoup(page.content, 'html.parser')
#     findDividends = soup.find("div", {"id": "history-container"})
#     return dividendsList

def scrape(symbol):
    #Initialize criteria
    price = sales = mktCap = eps = peRatio = pbRatio = currRatio = None
    grahamNum = assets = liabilities = epsList = None
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
    # dividendsList = fetchDividends(symbol)

    # TODO - Fetch the following, final criteria:
    # Get last 20 years of dividend history. If they have a dividend, check whether they've had consistent payments.
    # Determine if they ever missed a payment or paid a decreasing dividend
    # url = 'https://www.marketwatch.com/investing/stock/' + symbol.lower() + '/financials/cash-flow'
    # dividendList
    # TODO = Print this data to an excel document. Update each symbol per fetch
    # excel.update(symbol, None)

    # All values, used to simple bug testing.
    overallDict = {
        "assets": assets,
        "bvps": bvps,
        "currRatio": currRatio,
        "dividendList": dividendList,
        "eps": eps,
        "epsList": epsList,
        "grahamNum": grahamNum,
        "liabilities": liabilities,
        "mktCap": mktCap,
        "pbRatio": pbRatio,
        "peRatio": peRatio,
        "price": price,
        "sales": sales
    }
    # print("Overall: " + str(overallDict))

    score = alg.score(mktCap, sales, peRatio, currRatio, epsList, dividendList, assets, liabilities)
    print("Score: " + str(score) + "/7")
    grahamNum = None
    if bvps is not None and eps is not None:
        grahamNum = alg.grahamNum(eps, bvps)
        if grahamNum is not None:
            grahamNum = round(grahamNum, 2)
    print("GrahamNum/Price: " + str(grahamNum) + "/" + str(price))
    return

def commands(phrase):
    args = phrase.split(' ')
    symbol = str(args[0])
    scrape(symbol)
    return