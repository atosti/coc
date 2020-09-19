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

def scrape(symbol):
    #Initialize criteria
    price = shares = mktCap = eps = peRatio = currRatio = assets = liabilities = epsList = dividends = None
    # Elements are ordered from 2015 -> 2019
    assetList = epsList = dividendList = liabilitiesList = None
    # Yahoo Finance
    # Market Cap
    url = 'https://finance.yahoo.com/quote/' + symbol.lower()
    page = requests.get(url)
    soup = BeautifulSoup(page.content, 'html.parser')
    mktCap = soup.find("td", {"data-test": "MARKET_CAP-value"}).get_text(strip=True)
    if "T" in mktCap:
        mktCap = float(mktCap[:-1]) * 1000000000000
    elif "B" in mktCap:
        mktCap = float(mktCap[:-1]) * 1000000000
    elif "M" in mktCap:
        mktCap = float(mktCap[:-1]) * 1000000
    # Marketwatch
    url = 'https://www.marketwatch.com/investing/stock/' + symbol.lower() + '/financials'
    page = requests.get(url)
    soup = BeautifulSoup(page.content, 'html.parser')
    # Earnings Per Share (EPS)
    fetch = soup.find("a", {"data-ref": "ratio_Eps1YrAnnualGrowth"}).parent.parent.findChildren()
    for elem in fetch:
        curr = elem.find("div", {"class": "miniGraph"})
        if curr:
            # Elements are ordered from 2015 -> 2019
            values = json.loads(curr.get("data-chart"))["chartValues"]
            epsList = values
            eps = float(values[-1])

    url = 'https://www.marketwatch.com/investing/stock/' + symbol.lower() + '/financials/balance-sheet'
    page = requests.get(url)
    soup = BeautifulSoup(page.content, 'html.parser')
    # Price
    fetch = soup.find("div", {"class": "lastprice"}).findChildren()
    for elem in fetch:
        curr = elem.find("p", {"class": "data bgLast"})
        if curr:
            price = float(curr.get_text(strip=True))
    # Total Assets of last 5 years
    fetch = soup.find("tr", {"class": "totalRow"}).findChildren()
    for elem in fetch:
        curr = elem.find("div", {"class": "miniGraph"})
        if curr:
            # Elements are ordered from 2015 -> 2019
            values = json.loads(curr.get("data-chart"))["chartValues"]
            assetList = values
            assets = int(values[-1])
    # Liabilities
    fetch = soup.find("a", {"data-ref": "ratio_TotalLiabilitiesToTotalAssets"}).parent.parent.findChildren()
    for elem in fetch:
        curr = elem.find("div", {"class": "miniGraph"})
        if curr:
            # Elements are ordered from 2015 -> 2019
            values = json.loads(curr.get("data-chart"))["chartValues"]
            liabilitiesList = values
            liabilities = int(values[-1])
    # Current Ratio
    url = 'https://www.marketwatch.com/investing/stock/' + symbol.lower() + '/profile'
    page = requests.get(url)
    soup = BeautifulSoup(page.content, 'html.parser')
    fetch = soup.find(text='Current Ratio').parent.parent
    currRatio = float(fetch.find("p", {"class": "lastcolumn"}).get_text(strip=True))
    # P/E Ratio
    fetch = soup.find(text='P/E Current').parent.parent
    peRatio = float(fetch.find("p", {"class": "lastcolumn"}).get_text(strip=True))
    shares = int(mktCap / price)
    earnings = int(shares * eps)
    # TODO - Fetch the following, final criteria:
    url = 'https://www.marketwatch.com/investing/stock/' + symbol.lower() + '/financials/cash-flow'
    page = requests.get(url)
    soup = BeautifulSoup(page.content, 'html.parser')
    # dividendList
    score = alg.score(mktCap, peRatio, currRatio, epsList, dividends, assets, liabilities)
    # TODO = Print this data to an excel document. Update each symbol per fetch
    # print("MktCap: " + str(mktCap))
    # print("Price: " + str(price))
    # print("Shares: " + str(shares))
    # print("Earnings: " + str(earnings))
    # print("Curr Ratio: " + str(currRatio))
    # print("P/E Ratio: " + str(peRatio))
    # print("Assets: " + str(assets))
    # print(assetList)
    # print("Liabilities: " + str(liabilities))
    # print(liabilitiesList)
    # print("EPS: " + str(eps))
    # print(epsList)
    print("Score: " + str(score) + "/7")
    return

def commands(phrase):
    args = phrase.split(' ')
    symbol = str(args[0])
    scrape(symbol)
    return