import requests, json, webbrowser, locale, alg, excel
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
    mktCap = yfQuoteSearch(soup, 'MARKET_CAP-value')
    peRatio = yfQuoteSearch(soup, 'PE_RATIO-value')
    eps = yfQuoteSearch(soup, 'EPS_RATIO-value')
    # Div Yield can come in 2 locations, depending on symbol
    findYield = yfQuoteSearch(soup, 'TD_YIELD-value')
    findForwardDivYield = yfQuoteSearch(soup, 'DIVIDEND_AND_YIELD-value')
    divYield = None
    if findYield != None:
        item = findYield
        if item != None:
            divYield = item
    elif findForwardDivYield != None:
        # Separates Forward Dividend from Dividend Yield
        items = findForwardDivYield.split(' ')
        if items != None:
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
        # Handlers for Million/Billion/Trillion values
        if 'T' in item:
            item = float(locale.atof(item[:-1])) * 1000000000000
        elif 'B' in item:
            item = float(locale.atof(item[:-1])) * 1000000000
        elif 'M' in item:
            item = float(locale.atof(item[:-1])) * 1000000
        # Exceptions for dividend yield fetches
        elif '%' in item or '(' in item or ')' in item:
            item = item
        elif item != "N/A":
            item = float(locale.atof(item))
        else:
            item = None
    return item

def mwFinancialsSearch(soup, text):
    itemDict = {'item': None, 'itemList': None}
    found = soup.find(text = text)
    if found:
        item = None # Most recent year's value
        itemList = None # List of 5 previous years' values
        fetch = found.parent.parent.parent.findChildren()
        for elem in fetch:
            elemFound = elem.find('div', {'class': 'chart--financials'})
            if elemFound:
                itemList = elemFound.get('data-chart-data').split(',')
                itemList = [float(i) for i in itemList]
                if itemList[-1] != None:
                    item = float(itemList[-1])
                itemDict.update(itemList = itemList, item = item)
                break;
    return itemDict

# Marketwatch Company Profile scraper
def mwProfileSearch(soup, text):
    item = None
    found = soup.find(text=text)
    if text == 'Sector' and found:
        fetch = found.parent.parent.find('span', {'class': 'primary'})
        item = fetch.get_text(strip=True)
    elif found:
        fetch = found.parent.parent.find('td', {'class': 'w25'})
        if fetch:
            value = fetch.get_text(strip=True)
            if value != "N/A":
                item = float(locale.atof(value))
    return item

# MarketWatch Financials scraper
def fetchFinancials(symbol):
    financialsDict = {"eps": None, "epsList": None, "sales": None, "salesList": None}
    symbol = symbol.replace("-", ".") #Convert for URL
    url = 'https://www.marketwatch.com/investing/stock/' + symbol.lower() + '/financials'
    soup = getSoup(url)
    itemDict = mwFinancialsSearch(soup, 'EPS (Basic)')
    financialsDict.update(eps = itemDict['item'])
    financialsDict.update(epsList = itemDict['itemList'])
    itemDict = mwFinancialsSearch(soup, 'Sales/Revenue')
    financialsDict.update(sales = itemDict['item'])
    financialsDict.update(salesList = itemDict['itemList'])
    # print('Financials: ' + str(financialsDict))
    return financialsDict

# MarketWatch Company Cash Flow scraper
def fetchCashFlow(symbol):
    cashFlowDict = {'dividend': None, 'dividendList': None}
    symbol = symbol.replace('-', '.') # Convert for URL
    url = 'https://www.marketwatch.com/investing/stock/' + symbol.lower() + '/financials/cash-flow'
    soup = getSoup(url)
    itemDict = mwFinancialsSearch(soup, 'Cash Dividends Paid - Total')
    # Marketwatch seems to list all dividends as negative, so adjust values
    itemDict['item'] = abs(itemDict['item'])
    itemDict['itemList'] = [abs(i) for i in itemDict['itemList']]
    cashFlowDict.update(dividend = itemDict['item'])
    cashFlowDict.update(dividendList = itemDict['itemList'])
    return cashFlowDict

# Marketwatch Balance Sheet scraper
def fetchBalanceSheet(symbol):
    balanceSheetDict = {'price': None, 'assets': None, 'liabilities': None}
    symbol = symbol.replace('-', '.') #Convert for URL
    url = 'https://www.marketwatch.com/investing/stock/' + symbol.lower() + '/financials/balance-sheet'
    soup = getSoup(url)
    itemDict = mwFinancialsSearch(soup, 'Total Assets')
    balanceSheetDict.update(assets = itemDict['item'])
    itemDict = mwFinancialsSearch(soup, 'Total Liabilities')
    balanceSheetDict.update(liabilities = itemDict['item'])
    # Fetch the price from the top of the page
    price = soup.find('bg-quote', {'class': 'value'})
    if price:
        price = price.get_text(strip=True)
    balanceSheetDict.update(price = price)
    return balanceSheetDict

def fetchProfile(symbol):
    profileDict = {'currRatio': None, 'peRatio': None, 'pbRatio': None, 
        'sector': None}
    symbol = symbol.replace("-", ".") #Convert for URL
    url = 'https://www.marketwatch.com/investing/stock/' + symbol.lower() + '/profile'
    soup = getSoup(url)
    profileDict.update(currRatio = mwProfileSearch(soup, "Current Ratio"))
    profileDict.update(peRatio = mwProfileSearch(soup, "P/E Current"))
    profileDict.update(pbRatio = mwProfileSearch(soup, "Price to Book Ratio"))
    profileDict.update(sector = mwProfileSearch(soup, "Sector"))
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
    # Lists of annual values are ordered from 2015 -> 2019
    epsList = dividendList = []
    # TODO - Try to store all fetches into one Dict that is just appended to.
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
    sector = profileDict['sector']
    # If Yahoo fails to fetch a P/E ratio, use Marketwatch's value
    if peRatio == None:
        peRatio = profileDict['peRatio']
    # If Yahoo fails to fetch EPS, use Marketwatch's value
    if eps == None:
        eps = financialsDict['eps']
    cashFlowDict = fetchCashFlow(symbol)
    # TODO - Dividend is the sum of all dividends paid. Divide it by num. shares
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
        'sector': sector,
        'symbol': symbol
    }
    outputHandler(overallDict, healthResult, flags)
    return

def outputHandler(overallDict, healthResult, flags):
    symbol = overallDict['symbol']
    indent = '    '
    # Check for relevant flags, and output accordingly
    print(indent + 'Score: ' + str(overallDict['score']) + '/7')
    print(indent + healthResult)
    print(indent + 'GrahamNum/Price: ' + str(overallDict['grahamNum']) 
        + '/' + str(overallDict['price']))
    print(indent + 'Dividend Yield: ' + str(overallDict['divYield']))
    print(indent + 'Sector: ' + str(overallDict['sector']))
    # Debug flag
    if 'd' in flags:
        print(indent + 'Debug: ' + str(overallDict))
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