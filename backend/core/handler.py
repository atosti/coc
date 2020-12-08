import requests, json, webbrowser, locale, alg, excel
from bs4 import BeautifulSoup

locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')


def get_soup(url):
    page = requests.get(url)
    soup = BeautifulSoup(page.content, 'html.parser')
    return soup


# Yahoo Finance quote
def fetch_yahoo_quote(symbol):
    quote_dict = {'div_yield': None, 'eps': None, 'mkt_cap': None, 'pe_ratio': None}
    symbol = symbol.replace('.', '-')  # Convert for URL
    url = 'https://finance.yahoo.com/quote/' + symbol.lower()
    soup = get_soup(url)
    mkt_cap = yf_quote_search(soup, 'MARKET_CAP-value')
    pe_ratio = yf_quote_search(soup, 'PE_RATIO-value')
    eps = yf_quote_search(soup, 'EPS_RATIO-value')
    # Div Yield can come in 2 locations, depending on symbol
    find_yield = yf_quote_search(soup, 'TD_YIELD-value')
    find_forward_div_yield = yf_quote_search(soup, 'DIVIDEND_AND_YIELD-value')
    div_yield = None
    if find_yield != None:
        item = find_yield
        if item != None:
            div_yield = item
    elif find_forward_div_yield != None:
        # Separates Forward Dividend from Dividend Yield
        items = find_forward_div_yield.split(' ')
        if items != None:
            div_yield = items[1].replace('(', '').replace(')', '')
    quote_dict.update(div_yield=div_yield, eps=eps, mkt_cap=mkt_cap, pe_ratio=pe_ratio)
    return quote_dict


# Yahoo Finance key stats
def fetch_yahoo_bvps(symbol):
    bvps = None
    symbol = symbol.replace('.', '-')  # Convert for URL
    url = 'https://finance.yahoo.com/quote/' + symbol.upper() + '/key-statistics'
    soup = get_soup(url)
    find_bvps = soup.find(text='Book Value Per Share')
    if find_bvps:
        fetch = find_bvps.parent.parent.parent.findChildren()
        # TODO - Currently just grabs the 4th element. Find a better way.
        elem = fetch[3]
        value = elem.get_text(strip=True)
        if value != 'N/A':
            bvps = float(value)
    return bvps


def yf_quote_search(soup, text):
    item = None
    found = soup.find('td', {'data-test': text})
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
        elif item != 'N/A':
            item = float(locale.atof(item))
        else:
            item = None
    return item


def mw_financials_search(soup, text):
    item_dict = {'item': None, 'item_list': None}
    found = soup.find(text=text)
    if found:
        item = None  # Most recent year's value
        item_list = None  # List of 5 previous years' values
        fetch = found.parent.parent.parent.findChildren()
        for elem in fetch:
            elemFound = elem.find('div', {'class': 'chart--financials'})
            if elemFound:
                item_list = elemFound.get('data-chart-data').split(',')
                # TODO - Check for empty datacharts to prevent crashes
                item_list = [float(i) for i in item_list]
                if item_list[-1] != None:
                    item = float(item_list[-1])
                item_dict.update(item_list=item_list, item=item)
                break
    return item_dict


# Marketwatch Company Profile scraper
def mw_profile_search(soup, text):
    item = None
    found = soup.find(text=text)
    if text == 'Sector' and found:
        fetch = found.parent.parent.find('span', {'class': 'primary'})
        item = fetch.get_text(strip=True)
    elif found:
        fetch = found.parent.parent.find('td', {'class': 'w25'})
        if fetch:
            value = fetch.get_text(strip=True)
            if value != 'N/A':
                item = float(locale.atof(value))
    return item


# MarketWatch Financials scraper
def fetch_financials(symbol):
    financials_dict = {'eps': None, 'eps_list': None, 'sales': None, 'sales_list': None}
    symbol = symbol.replace('-', '.')  # Convert for URL
    url = (
        'https://www.marketwatch.com/investing/stock/' + symbol.lower() + '/financials'
    )
    soup = get_soup(url)
    item_dict = mw_financials_search(soup, 'EPS (Basic)')
    financials_dict.update(eps=item_dict['item'])
    financials_dict.update(eps_list=item_dict['item_list'])
    item_dict = mw_financials_search(soup, 'Sales/Revenue')
    financials_dict.update(sales=item_dict['item'])
    financials_dict.update(sales_list=item_dict['item_list'])
    # print('Financials: ' + str(financials_dict))
    return financials_dict


# MarketWatch Company Cash Flow scraper
def fetch_cash_flow(symbol):
    cash_flow_dict = {'dividend': None, 'dividend_list': None}
    symbol = symbol.replace('-', '.')  # Convert for URL
    url = (
        'https://www.marketwatch.com/investing/stock/'
        + symbol.lower()
        + '/financials/cash-flow'
    )
    soup = get_soup(url)
    item_dict = mw_financials_search(soup, 'Cash Dividends Paid - Total')
    # Marketwatch seems to list all dividends as negative, so adjust values
    item_dict['item'] = abs(item_dict['item'])
    item_dict['item_list'] = [abs(i) for i in item_dict['item_list']]
    cash_flow_dict.update(dividend=item_dict['item'])
    cash_flow_dict.update(dividend_list=item_dict['item_list'])
    return cash_flow_dict


# Marketwatch Balance Sheet scraper
def fetch_balance_sheet(symbol):
    balance_sheet_dict = {'price': None, 'assets': None, 'liabilities': None}
    symbol = symbol.replace('-', '.')  # Convert for URL
    url = (
        'https://www.marketwatch.com/investing/stock/'
        + symbol.lower()
        + '/financials/balance-sheet'
    )
    soup = get_soup(url)
    item_dict = mw_financials_search(soup, 'Total Assets')
    balance_sheet_dict.update(assets=item_dict['item'])
    item_dict = mw_financials_search(soup, 'Total Liabilities')
    balance_sheet_dict.update(liabilities=item_dict['item'])
    # Fetch the price from the top of the page
    price = soup.find('bg-quote', {'class': 'value'})
    if price:
        price = price.get_text(strip=True)
    balance_sheet_dict.update(price=price)
    return balance_sheet_dict


def fetch_profile(symbol):
    profile_dict = {'curr_ratio': None, 'pe_ratio': None, 'pb_ratio': None, 'sector': None}
    symbol = symbol.replace('-', '.')  # Convert for URL
    url = 'https://www.marketwatch.com/investing/stock/' + symbol.lower() + '/company-profile'
    soup = get_soup(url)
    profile_dict.update(curr_ratio=mw_profile_search(soup, 'Current Ratio'))
    profile_dict.update(pe_ratio=mw_profile_search(soup, 'P/E Current'))
    profile_dict.update(pbRatio=mw_profile_search(soup, 'Price to Book Ratio'))
    profile_dict.update(sector=mw_profile_search(soup, 'Sector'))
    # print('Profile: ' + str(profile_dict))
    return profile_dict


def score_summation(
    good_assets,
    good_curr_ratio,
    good_dividend,
    good_eps,
    good_eps_growth,
    good_pe_ratio,
    good_sales,
):
    score = 0
    if good_assets:
        score += 1
    if good_curr_ratio:
        score += 1
    if good_dividend:
        score += 1
    if good_eps:
        score += 1
    if good_eps_growth:
        score += 1
    if good_pe_ratio:
        score += 1
    if good_sales:
        score += 1
    return score


def scrape(symbol, flags):
    # Initialize criteria
    price = sales = mkt_cap = eps = pe_ratio = pb_ratio = curr_ratio = None
    graham_num = assets = liabilities = eps_list = None
    # Lists of annual values are ordered from 2015 -> 2019
    eps_list = dividend_list = []
    # TODO - Try to store all fetches into one Dict that is just appended to.
    # Website scraping
    quote_dict = fetch_yahoo_quote(symbol)
    mkt_cap = quote_dict['mkt_cap']
    pe_ratio = quote_dict['pe_ratio']
    eps = quote_dict['eps']
    div_yield = quote_dict['div_yield']
    bvps = fetch_yahoo_bvps(symbol)
    financials_dict = fetch_financials(symbol)
    eps_list = financials_dict['eps_list']
    sales = financials_dict['sales']
    balance_sheet_dict = fetch_balance_sheet(symbol)
    price = balance_sheet_dict['price']
    assets = balance_sheet_dict['assets']
    liabilities = balance_sheet_dict['liabilities']
    profile_dict = fetch_profile(symbol)
    curr_ratio = profile_dict['curr_ratio']
    pb_ratio = profile_dict['pb_ratio']
    sector = profile_dict['sector']
    # If Yahoo fails to fetch a P/E ratio, use Marketwatch's value
    if pe_ratio == None:
        pe_ratio = profile_dict['pe_ratio']
    # If Yahoo fails to fetch EPS, use Marketwatch's value
    if eps == None:
        eps = financials_dict['eps']
    cash_flow_dict = fetch_cash_flow(symbol)
    # TODO - Dividend is the sum of all dividends paid. Divide it by num. shares
    dividend = cash_flow_dict['dividend']
    dividend_list = cash_flow_dict['dividend_list']
    # Check the company against the core criteria
    health_result = alg.health_check(
        mkt_cap,
        sales,
        pe_ratio,
        curr_ratio,
        eps_list,
        dividend,
        dividend_list,
        assets,
        liabilities,
    )
    good_assets = alg.good_assets(mkt_cap, assets, liabilities)
    good_curr_ratio = alg.good_curr_ratio(curr_ratio)
    good_dividend = alg.good_dividend(dividend, dividend_list)
    good_eps = alg.good_eps(eps_list)
    good_eps_growth = alg.good_eps_growth(eps_list)
    good_pe_ratio = alg.good_pe_ratio(pe_ratio)
    good_sales = alg.good_sales(sales)
    score = score_summation(
        good_assets,
        good_curr_ratio,
        good_dividend,
        good_eps,
        good_eps_growth,
        good_pe_ratio,
        good_sales,
    )
    graham_num = None
    if bvps is not None and eps is not None:
        graham_num = alg.graham_num(eps, bvps)
        if graham_num is not None:
            graham_num = round(graham_num, 2)
    # All values, used to do simple debugging.
    overall_dict = {
        'assets': assets,
        'bvps': bvps,
        'curr_ratio': curr_ratio,
        'dividend': dividend,
        'dividend_list': dividend_list,
        'div_yield': div_yield,
        'eps': eps,
        'eps_list': eps_list,
        'good_assets': good_assets,
        'good_curr_ratio': good_curr_ratio,
        'good_dividend': good_dividend,
        'good_eps': good_eps,
        'good_eps_growth': good_eps_growth,
        'good_pe_ratio': good_pe_ratio,
        'good_sales': good_sales,
        'graham_num': graham_num,
        'liabilities': liabilities,
        'mkt_cap': mkt_cap,
        'pb_ratio': pb_ratio,
        'pe_ratio': pe_ratio,
        'price': price,
        'sales': sales,
        'score': score,
        'sector': sector,
        'symbol': symbol,
    }
    output_handler(overall_dict, health_result, flags)
    return


def output_handler(overall_dict, health_result, flags):
    symbol = overall_dict['symbol']
    indent = "    "
    # Check for relevant flags, and output accordingly
    print(indent + 'Score: ' + str(overall_dict['score']) + '/7')
    print(indent + health_result)
    print(
        indent
        + 'Graham Num/Price: '
        + str(overall_dict['graham_num'])
        + '/'
        + str(overall_dict['price'])
    )
    print(indent + 'Dividend Yield: ' + str(overall_dict['div_yield']))
    print(indent + 'Sector: ' + str(overall_dict['sector']))
    # Debug flag
    if 'd' in flags:
        print(indent + 'Debug: ' + str(overall_dict))
    # Excel update flag
    if 'x' in flags:
        excel.update(symbol, overall_dict)
    return


# Assembles a list of flags passed as arguments
def flag_handler(args):
    flags = []
    for arg in args:
        if arg[:1] == '-':
            for flag in arg[1:]:
                flags.append(flag)
    return flags


def commands(phrase):
    args = phrase.split(' ')
    symbol = str(args[0])
    flags = flag_handler(args)
    scrape(symbol, flags)
    return
