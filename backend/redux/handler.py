import requests, json, webbrowser, alg, excel, locale
from bs4 import BeautifulSoup
locale.setlocale(locale.LC_ALL, 'en_US.UTF-8') 

def getSoup(url):
    page = requests.get(url)
    soup = BeautifulSoup(page.content, 'html.parser')
    return soup

# Yahoo Finance quote
def fetchYahooQuote(symbol):
    quoteDict = {'divYield': None, 'eps': None, 'mktCap': None, 'peRatio': None}
    symbol = symbol.replace(".", "-") #Convert for URL
    url = 'https://finance.yahoo.com/quote/' + symbol.lower()
    soup = getSoup(url)
    mktCap = yfQuoteSearch(soup, "MARKET_CAP-value")
    peRatio = yfQuoteSearch(soup, "PE_RATIO-value")
    eps = yfQuoteSearch(soup, "EPS_RATIO-value")
    # Separate Forward Dividend from Dividend Yield
    forwardDivYield = yfQuoteSearch(soup, "DIVIDEND_AND_YIELD-value")
    if forwardDivYield != None:
        items = forwardDivYield.split(' ')
    else:
        items = None
    divYield = items[1].replace('(', '').replace(')', '')
    quoteDict.update(divYield = divYield, eps = eps, mktCap = mktCap, 
        peRatio = peRatio)
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
        if 'T' in item:
            item = float(locale.atof(item[:-1])) * 1000000000000
        elif 'B' in item:
            item = float(locale.atof(item[:-1])) * 1000000000
        elif 'M' in item:
            item = float(locale.atof(item[:-1])) * 1000000
        elif '(' in item or ')' in item:
            item = item
        elif item != "N/A":
            item = float(locale.atof(item))
        else:
            item = None
    return item

def mwFinancialsSearch(soup, text):
    itemDict = {"item": None, "itemList": None}
    found = soup.find("a", {"data-ref": text})
    if found:
        item = None
        itemList = None
        fetch = found.parent.parent.findChildren()
        for elem in fetch:
            elemFound = elem.find("div", {"class": "miniGraph"})
            if elemFound:
                values = json.loads(elemFound.get("data-chart"))["chartValues"]
                itemList = values
                if values[-1] != None:
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
                item = float(locale.atof(value))
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

# MarketWatch Company Cash Flow scraper
def fetchCashFlow(symbol):
    cashFlowDict = {"dividend": None, "dividendList": None}
    symbol = symbol.replace("-", ".") #Convert for URL
    url = "https://www.marketwatch.com/investing/stock/" + symbol.lower() + "/financials/cash-flow"
    soup = getSoup(url)
    found = soup.find(text='Cash Dividends Paid - Total')
    if found:
        fetch = found.parent.parent.findChildren()
        item = None
        itemList = None
        for elem in fetch:
            elemFound = elem.find("div", {"class": "miniGraph"})
            if elemFound:
                values = json.loads(elemFound.get("data-chart"))["chartValues"]
                itemList = values
                # Dividends are fetched as negative on MW, so convert them
                for i in range(0, len(itemList)):
                    if itemList[i] != None:
                        itemList[i] = abs(itemList[i])
                if values[-1] != None:
                    item = abs(float(values[-1]))
                cashFlowDict.update(dividendList = itemList, dividend = item)
    return cashFlowDict

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

def scoreSummation(goodAssets, goodCurrRatio, goodDividend, goodEps,
    goodEpsGrowth, goodPeRatio, goodSales):
    score = 0
    if(goodAssets):
        score += 1
    if(goodCurrRatio):
        score += 1
    if(goodDividend):
        score += 1
    if(goodEps):
        score += 1
    if(goodEpsGrowth):
        score += 1
    if(goodPeRatio):
        score += 1
    if(goodSales):
        score += 1
    return score

def scrape(symbol, flags):
    #Initialize criteria
    price = sales = mktCap = eps = peRatio = pbRatio = currRatio = None
    grahamNum = assets = liabilities = epsList = None
    # List elements are ordered from 2015 -> 2019
    epsList = dividendList = []
    # Website scraping
    quoteDict = fetchYahooQuote(symbol)
    mktCap = quoteDict['mktCap']
    peRatio = quoteDict['peRatio']
    eps = quoteDict['eps']
    divYield = quoteDict['divYield']
    bvps = fetchYahooBvps(symbol)
    financialsDict = fetchFinancials(symbol)
    epsList = financialsDict['epsList']
    sales = financialsDict['sales']
    balanceSheetDict = fetchBalanceSheet(symbol)
    price = balanceSheetDict['price']
    assets = balanceSheetDict['assets']
    liabilities = balanceSheetDict['liabilities']
    profileDict = fetchProfile(symbol)
    currRatio = profileDict['currRatio']
    pbRatio = profileDict['pbRatio']
    # If Yahoo failed to fetch the P/E ratio, use Marketwatch's
    if peRatio == None:
        peRatio = profileDict['peRatio']
    cashFlowDict = fetchCashFlow(symbol)
    dividend = cashFlowDict['dividend']
    dividendList = cashFlowDict['dividendList']
    # Check the company against the core criteria
    healthResult = alg.healthCheck(mktCap, sales, peRatio, currRatio, epsList, 
        dividend, dividendList, assets, liabilities)
    goodAssets = alg.goodAssets(mktCap, assets, liabilities)
    goodCurrRatio = alg.goodCurrRatio(currRatio)
    goodDividend = alg.goodDividend(dividend, dividendList)
    goodEps = alg.goodEps(epsList)
    goodEpsGrowth = alg.goodEpsGrowth(epsList)
    goodPeRatio = alg.goodPeRatio(peRatio)
    goodSales = alg.goodSales(sales)
    score = scoreSummation(goodAssets, goodCurrRatio, goodDividend, goodEps,
        goodEpsGrowth, goodPeRatio, goodSales)
    grahamNum = None
    if bvps is not None and eps is not None:
        grahamNum = alg.grahamNum(eps, bvps)
        if grahamNum is not None:
            grahamNum = round(grahamNum, 2)
    # All values, used to do simple debugging.
    overallDict = {
        'assets': assets,
        'bvps': bvps,
        'currRatio': currRatio,
        'dividend': dividend,
        'dividendList': dividendList,
        'divYield': divYield,
        'eps': eps,
        'epsList': epsList,
        'goodAssets': goodAssets,
        'goodCurrRatio': goodCurrRatio,
        'goodDividend': goodDividend,
        'goodEps': goodEps,
        'goodEpsGrowth': goodEpsGrowth,
        'goodPeRatio': goodPeRatio,
        'goodSales': goodSales,
        'grahamNum': grahamNum,
        'liabilities': liabilities,
        'mktCap': mktCap,
        'pbRatio': pbRatio,
        'peRatio': peRatio,
        'price': price,
        'sales': sales,
        'score': score,
        'symbol': symbol
    }
    outputHandler(overallDict, healthResult, flags)
    return

def outputHandler(overallDict, healthResult, flags):
    grahamNum = overallDict["grahamNum"]
    price = overallDict["price"]
    score = overallDict["score"]
    symbol = overallDict["symbol"]
    # Check for relevant flags, and output accordingly
    print(healthResult)
    print('Score: ' + str(score) + '/7')
    print('GrahamNum/Price: ' + str(grahamNum) + '/' + str(price))
    print('Dividend Yield: ' + str(overallDict['divYield']))
    # Debug flag
    if 'd' in flags:
        print('Debug: ' + str(overallDict))
    # Excel update flag
    if 'x' in flags:
        excel.update(symbol, overallDict)
    return

# Assembles a list of flags passed as arguments
def flagHandler(args):
    flags = []
    for arg in args:
        if arg[:1] == '-':
            for flag in arg[1:]:
                flags.append(flag)
    return flags
    
def commands(phrase):
    args = phrase.split(' ')
    symbol = str(args[0])
    flags = flagHandler(args)
    scrape(symbol, flags)
    return