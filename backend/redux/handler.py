import requests, json, webbrowser, alg, excel, locale
from bs4 import BeautifulSoup
locale.setlocale(locale.LC_ALL, 'en_US.UTF-8') 

def getSoup(url):
    page = requests.get(url)
    soup = BeautifulSoup(page.content, 'html.parser')
    return soup

# Yahoo Finance quote
def fetchYahooQuote(symbol):
    quoteDict = {"mktCap": None, "peRatio": None, "eps": None}
    symbol = symbol.replace(".", "-") #Convert for URL
    url = 'https://finance.yahoo.com/quote/' + symbol.lower()
    soup = getSoup(url)
    mktCap = yfQuoteSearch(soup, "MARKET_CAP-value")
    peRatio = yfQuoteSearch(soup, "PE_RATIO-value")
    eps = yfQuoteSearch(soup, "EPS_RATIO-value")
    quoteDict.update(mktCap = mktCap, peRatio = peRatio, eps = eps)
    return quoteDict

# Yahoo Finance key stats
def fetchYahooBvps(symbol):
    bvps = None
    symbol = symbol.replace(".", "-") #Convert for URL
    url = 'https://finance.yahoo.com/quote/' + symbol.upper() + '/key-statistics'
    soup = getSoup(url)
    # findBvps = soup.find("td", {"data-reactid": "599"})
    findBvps = soup.find(text='Book Value Per Share')
    if findBvps:
        fetch = findBvps.parent.parent.parent.findChildren()
        # TODO - Currently just grabs the 4th element. Find a better way.
        elem = fetch[3]
        value = elem.get_text(strip=True)
        if value != "N/A":
            bvps = float(value)
    return bvps

def yfQuoteSearch(soup, text):
    item = None
    found = soup.find("td", {"data-test": text})
    if found:
        item = found.get_text(strip=True)
        if "T" in item:
            item = float(locale.atof(item[:-1])) * 1000000000000
        elif "B" in item:
            item = float(locale.atof(item[:-1])) * 1000000000
        elif "M" in item:
            item = float(locale.atof(item[:-1])) * 1000000
        elif item != "N/A":
            item = float(locale.atof(item))
        else:
            item = None
    return item

def mwFinancialsSearch(soup, text):
    itemDict = {"item": None, "itemList": None}
    found = soup.find("a", {"data-ref": text})
    if found:
        fetch = found.parent.parent.findChildren()
        # print(fetch)
        for elem in fetch:
            elemFound = elem.find("div", {"class": "miniGraph"})
            if elemFound:
                values = json.loads(elemFound.get("data-chart"))["chartValues"]
                itemList = values
                item = float(values[-1])
                itemDict.update(itemList = itemList, item = item)
    return itemDict

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

def fetchFinancials(symbol):
    financialsDict = {"eps": None, "epsList": None, "sales": None, "salesList": None}
    symbol = symbol.replace("-", ".") #Convert for URL
    url = 'https://www.marketwatch.com/investing/stock/' + symbol.lower() + '/financials'
    soup = getSoup(url)
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
    symbol = symbol.replace("-", ".") #Convert for URL
    url = 'https://www.marketwatch.com/investing/stock/' + symbol.lower() + '/financials/balance-sheet'
    soup = getSoup(url)
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
    findLiabilites = soup.find(text=' Total Liabilities')
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

def fetchProfile(symbol):
    profileDict = {"currRatio": None, "peRatio": None, "pbRatio": None}
    symbol = symbol.replace("-", ".") #Convert for URL
    url = 'https://www.marketwatch.com/investing/stock/' + symbol.lower() + '/profile'
    soup = getSoup(url)
    profileDict.update(currRatio = mwProfileSearch(soup, "Current Ratio"))
    profileDict.update(peRatio = mwProfileSearch(soup, "P/E Current"))
    profileDict.update(pbRatio = mwProfileSearch(soup, "Price to Book Ratio"))
    # print("Profile: " + str(profileDict))
    return profileDict

# FIXME - Finish this
def fetchCashFlow(symbol):
    cashFlowDict = {"dividend": None, "dividendList": None}
    symbol = symbol.replace("-", ".") #Convert for URL
    url = "https://www.marketwatch.com/investing/stock/" + symbol + "/financials/cash-flow"
    soup = getSoup(url)
    itemDict = mwFinancialsSearch(soup, "Cash Dividends Paid - Total")
    # print("ItemDict: " + str(itemDict))
    cashFlowDict.update(dividend = itemDict["item"])
    cashFlowDict.update(dividendList = itemDict["itemList"])
    return cashFlowDict

def scrape(symbol):
    #Initialize criteria
    price = sales = mktCap = eps = peRatio = pbRatio = currRatio = None
    grahamNum = assets = liabilities = epsList = None
    # List elements are ordered from 2015 -> 2019
    epsList = dividendList = []
    # Website scraping
    quoteDict = fetchYahooQuote(symbol)
    mktCap = quoteDict["mktCap"]
    peRatio = quoteDict["peRatio"]
    eps = quoteDict["eps"]
    bvps = fetchYahooBvps(symbol)
    financialsDict = fetchFinancials(symbol)
    epsList = financialsDict["epsList"]
    sales = financialsDict["sales"]
    balanceSheetDict = fetchBalanceSheet(symbol)
    price = balanceSheetDict["price"]
    assets = balanceSheetDict["assets"]
    liabilities = balanceSheetDict["liabilities"]
    profileDict = fetchProfile(symbol)
    currRatio = profileDict["currRatio"]
    pbRatio = profileDict["pbRatio"]
    cashFlowDict = fetchCashFlow(symbol)
    dividend = cashFlowDict["dividend"]
    dividendList = cashFlowDict["dividendList"]
    print("Dividends: " + str(dividendList))
    print("Dividend: " + str(dividend))

    # TODO - Fetch the following, final criteria:
    # Get last 20 years of dividend history. If they have a dividend, check whether they've had consistent payments.
    # Determine if they ever missed a payment or paid a decreasing dividend
    # dividendList
    # TODO = Print this data to an excel document. Update each symbol per fetch
    # excel.update(symbol, None)

    # https://www.marketbeat.com/stocks/NYSE/WLKP/dividend/

    score = alg.score(mktCap, sales, peRatio, currRatio, epsList, dividendList, assets, liabilities)
    print("Score: " + str(score) + "/7")
    grahamNum = None
    if bvps is not None and eps is not None:
        grahamNum = alg.grahamNum(eps, bvps)
        if grahamNum is not None:
            grahamNum = round(grahamNum, 2)
    print("GrahamNum/Price: " + str(grahamNum) + "/" + str(price))

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
    return

def commands(phrase):
    args = phrase.split(' ')
    symbol = str(args[0])
    scrape(symbol)
    return