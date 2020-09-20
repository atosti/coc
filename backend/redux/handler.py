import requests, json, webbrowser, alg
from bs4 import BeautifulSoup

# headers = requests.utils.default_headers()
# headers.update({
#     'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:52.0) Gecko/20100101 Firefox/52.0',
# })

# def captchaHandler(soup):
#     code = ""
#     captchaExists = soup.find("div", {"class": "g-recaptcha"})
#     if captchaExists:
#         captchaUrl = soup.find("iframe")["src"]
#         sitekey = soup.find("div", {"class": "g-recaptcha"})["data-sitekey"]
#         webbrowser.open(captchaUrl)
#         # User enters code after completing captcha
#         print('Enter the captcha code from your browser: ')
#         print('$', end='')
#         code = input()
#         # Put code into the response and submit the form
#         # data = {"g-recaptcha-response": code}
#         # data = {"secret": sitekey, "response": code}
#         # page = requests.post(captchaUrl, data = data)
#         # tmp = BeautifulSoup(page.content, 'html.parser')
#         # print(tmp)
#         # return True
#     return code

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
    profileDict = {"currRatio": None, "peRatio": None}
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
    return profileDict

def scrape(symbol):
    #Initialize criteria
    price = sales = mktCap = eps = peRatio = currRatio = None
    assets = liabilities = epsList = dividends = None
    # Elements are ordered from 2015 -> 2019
    epsList = dividendList = []
    # Yahoo Finance Market Cap
    mktCap = fetchMktCap(symbol)
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

    # TODO - Fetch the following, final criteria:
    # url = 'https://www.marketwatch.com/investing/stock/' + symbol.lower() + '/financials/cash-flow'
    # page = requests.get(url)
    # soup = BeautifulSoup(page.content, 'html.parser')
    # dividendList
    
    # TODO = Print this data to an excel document. Update each symbol per fetch
    # print("MktCap: " + str(mktCap))
    # print("Price: " + str(price))
    # print("Earnings: " + str(earnings))
    # print("Curr Ratio: " + str(currRatio))
    # print("P/E Ratio: " + str(peRatio))
    # print("Assets: " + str(assets))
    # print(assetList)
    # print("Liabilities: " + str(liabilities))
    # print(liabilitiesList)
    # print("EPS: " + str(eps))
    # print(epsList)

    score = alg.score(mktCap, sales, peRatio, currRatio, epsList, dividends, assets, liabilities)
    print("Score: " + str(score) + "/7")
    return

def commands(phrase):
    args = phrase.split(' ')
    symbol = str(args[0])
    scrape(symbol)
    return