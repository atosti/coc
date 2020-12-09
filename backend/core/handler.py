import requests, json, webbrowser, locale, alg, excel
from bs4 import BeautifulSoup

locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')


def get_soup(url):
    page = requests.get(url)
    soup = BeautifulSoup(page.content, 'html.parser')
    return soup


# Dividend yield HTML has 2 locations for div_yield on Yahoo Finance
def yf_quote_fetch_div_yield(soup):
    div_yield = yf_quote_search(soup, 'TD_YIELD-value')
    if div_yield == None:
        items = yf_quote_search(soup, 'DIVIDEND_AND_YIELD-value')
        if items != None:
            # Separates forward dividend from dividend yield
            items = items.split(' ')
            div_yield = items[1].replace('(', '').replace(')', '')
    return div_yield


# Yahoo Finance scrape for: 'finance.yahoo.com/quote/symbol'
def scrape_yahoo_quote(symbol):
    quote_dict = {'div_yield': None, 'eps': None, 'mkt_cap': None, 'pe_ratio': None}
    symbol = symbol.replace('.', '-')  # Convert for URL
    url = 'https://finance.yahoo.com/quote/' + symbol.lower()
    soup = get_soup(url)
    mkt_cap = yf_quote_search(soup, 'MARKET_CAP-value')
    pe_ratio = yf_quote_search(soup, 'PE_RATIO-value')
    eps = yf_quote_search(soup, 'EPS_RATIO-value')
    div_yield = yf_quote_fetch_div_yield(soup)
    quote_dict.update(div_yield=div_yield, eps=eps, mkt_cap=mkt_cap, pe_ratio=pe_ratio)
    return quote_dict


# Yahoo Finance scrape for: 'finance.yahoo.com/quote/symbol/key-statistics'
def scrape_yahoo_key_stats(symbol):
    # bvps = None
    key_stats_dict = {'bvps': None}
    symbol = symbol.replace('.', '-')  # Convert for URL
    url = 'https://finance.yahoo.com/quote/' + symbol.lower() + '/key-statistics'
    soup = get_soup(url)
    find_bvps = soup.find(text='Book Value Per Share')
    if find_bvps:
        fetch = find_bvps.parent.parent.parent.findChildren()
        # TODO - Currently just grabs the 4th element. Find a better way to nav.
        elem = fetch[3]
        value = elem.get_text(strip=True)
        if value != 'N/A':
            bvps = float(value)
    key_stats_dict.update(bvps=bvps)
    return key_stats_dict


# Takes a fetched string number, such as '700M', and converts it to a float
def str_to_num(num):
    raw_num = None
    if 'T' in num:
        raw_num = float(locale.atof(num[:-1])) * 1000000000000
    elif 'B' in num:
        raw_num = float(locale.atof(num[:-1])) * 1000000000
    elif 'M' in num:
        raw_num = float(locale.atof(num[:-1])) * 1000000
    elif num != 'N/A':
        raw_num = float(locale.atof(num))
    return raw_num


def yf_quote_search(soup, text):
    item = None
    found = soup.find('td', {'data-test': text})
    if found:
        item = found.get_text(strip=True)
        special_values = ['%', '(', ')']
        if not any(value in item for value in special_values):
            item = str_to_num(item)
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
                item_list = [float(i) for i in item_list if i != '']
                if len(item_list) > 0 and item_list[-1] != None:
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


# MarketWatch scraper for: 'marketwatch.com/investing/stock/symbol/financials'
def scrape_mw_financials(symbol):
    financials_dict = {'eps': None, 'eps_list': None, 'sales': None, 
        'sales_list': None
    }
    symbol = symbol.replace('-', '.')  # Convert for URL
    url = (
        'https://www.marketwatch.com/investing/stock/' + symbol.lower() + '/financials'
    )
    soup = get_soup(url)
    item_dict = mw_financials_search(soup, 'EPS (Basic)')
    # Only overwrites EPS if it has a non nonetype value
    eps = item_dict['item']
    if eps != None:
        financials_dict.update(eps=eps)
    financials_dict.update(eps_list=item_dict['item_list'])
    item_dict = mw_financials_search(soup, 'Sales/Revenue')
    financials_dict.update(sales=item_dict['item'])
    financials_dict.update(sales_list=item_dict['item_list'])
    return financials_dict


# MarketWatch scraper for: 'marketwatch.com/investing/stock/symbol/financials/cash-flow'
def scrape_mw_cash_flow(symbol):
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
    if item_dict['item'] != None:
        item_dict['item'] = abs(item_dict['item'])
    if item_dict['item_list'] != None:
        item_dict['item_list'] = [abs(i) for i in item_dict['item_list']]
    cash_flow_dict.update(dividend=item_dict['item'])
    cash_flow_dict.update(dividend_list=item_dict['item_list'])
    return cash_flow_dict


# MarketWatch scraper for: 'marketwatch.com/investing/stock/symbol/financials/balance-sheet'
def scrape_mw_balance_sheet(symbol):
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
    price = None
    intraday_price = soup.find('h3', {'class': 'intraday__price'})
    if intraday_price:
        price = intraday_price.get_text(strip=True).replace('$', '')
    balance_sheet_dict.update(price=price)
    return balance_sheet_dict


# MarketWatch scraper for: 'marketwatch.com/investing/stock/symbol/company-profile'
def scrape_mw_profile(symbol):
    profile_dict = {'curr_ratio': None, 'pe_ratio': None, 'pb_ratio': None, 'sector': None}
    symbol = symbol.replace('-', '.')  # Convert for URL
    url = 'https://www.marketwatch.com/investing/stock/' + symbol.lower() + '/company-profile'
    soup = get_soup(url)
    profile_dict.update(curr_ratio=mw_profile_search(soup, 'Current Ratio'))
    # Only overwrites PE ratio if it has a non nonetype value
    pe_ratio = mw_profile_search(soup, 'P/E Current')
    if pe_ratio != None:
        profile_dict.update(pe_ratio=pe_ratio)
    profile_dict.update(pbRatio=mw_profile_search(soup, 'Price to Book Ratio'))
    profile_dict.update(sector=mw_profile_search(soup, 'Sector'))
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


def total_score(overall_dict):
    good_assets = alg.good_assets(
        overall_dict['mkt_cap'],
        overall_dict['assets'],
        overall_dict['liabilities']
    )
    good_curr_ratio = alg.good_curr_ratio(overall_dict['curr_ratio'])
    good_dividend = alg.good_dividend(
        overall_dict['dividend'], 
        overall_dict['dividend_list']
    )
    good_eps = alg.good_eps(overall_dict['eps_list'])
    good_eps_growth = alg.good_eps_growth(overall_dict['eps_list'])
    good_pe_ratio = alg.good_pe_ratio(overall_dict['pe_ratio'])
    good_sales = alg.good_sales(overall_dict['sales'])
    score = score_summation(
        good_assets,
        good_curr_ratio,
        good_dividend,
        good_eps,
        good_eps_growth,
        good_pe_ratio,
        good_sales,
    )
    return score


def check(symbol, flags):
    # Website scraping into a single dict
    # Notes: a. Lists of annual values are ordered from 2015 -> 2019
    #        b. EPS and PE ratio are overwritten by Yahoo nums if also in MW
    overall_dict = {
        'symbol': symbol,
        **scrape_mw_financials(symbol),
        **scrape_mw_balance_sheet(symbol),
        **scrape_mw_profile(symbol),
        **scrape_mw_cash_flow(symbol),
        **scrape_yahoo_quote(symbol),
        **scrape_yahoo_key_stats(symbol),
    }
    overall_dict.update(
        graham_num=alg.graham_num(overall_dict['eps'], overall_dict['bvps'])
    )
    # TODO - Dividend is the sum of all dividends paid. Divide it by num. shares
    health_result = alg.health_check(
        overall_dict['mkt_cap'],
        overall_dict['sales'],
        overall_dict['pe_ratio'],
        overall_dict['curr_ratio'],
        overall_dict['eps_list'],
        overall_dict['dividend'],
        overall_dict['dividend_list'],
        overall_dict['assets'],
        overall_dict['liabilities'],
    )
    score = total_score(overall_dict)
    overall_dict.update(score=score)
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
        + str(round(overall_dict['graham_num'], 2))
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
    check(symbol, flags)
    return
