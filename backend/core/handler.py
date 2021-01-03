import requests, json, webbrowser, locale
from bs4 import BeautifulSoup
from requests.auth import HTTPBasicAuth
from rich import print
from pprint import pprint
import re
from backend.core import alg, excel


locale.setlocale(locale.LC_ALL, "en_US.UTF-8")


def get_soup(url, user="", password=""):
    if user != "" and password != "":
        page = requests.get(url, auth=(user, password))
    else:
        page = requests.get(url)
    soup = BeautifulSoup(page.content, "html.parser")
    return soup


# Dividend yield HTML has 2 locations for div_yield on Yahoo Finance
def yf_quote_fetch_div_yield(soup):
    div_yield = yf_quote_search(soup, "TD_YIELD-value")
    if div_yield == None:
        items = yf_quote_search(soup, "DIVIDEND_AND_YIELD-value")
        if items != None:
            # Separates forward dividend from dividend yield
            items = items.split(" ")
            div_yield = items[1].replace("(", "").replace(")", "")
    return div_yield


# Yahoo Finance scrape for: 'https://finance.yahoo.com/quote/symbol'
def scrape_yahoo_quote(symbol):
    soup = get_soup(
        f"https://finance.yahoo.com/quote/{symbol.replace('.', '-').lower()}"
    )
    return {
        "div_yield": yf_quote_fetch_div_yield(soup),
        "eps": yf_quote_search(soup, "EPS_RATIO-value"),
        "mkt_cap": yf_quote_search(soup, "MARKET_CAP-value"),
        "pe_ratio": yf_quote_search(soup, "PE_RATIO-value"),
    }


# Yahoo Finance scrape for: 'https://finance.yahoo.com/quote/symbol/key-statistics'
def scrape_yahoo_key_stats(symbol):
    soup = get_soup(
        f"https://finance.yahoo.com/quote/{symbol.replace('.', '-').lower()}/key-statistics"
    )
    find_bvps = soup.find(text="Book Value Per Share")
    if find_bvps:
        fetch = find_bvps.parent.parent.parent.findChildren()
        # TODO - Currently just grabs the 4th element. Find a better way to nav.
        elem = fetch[3]
        value = elem.get_text(strip=True)
        if value != "N/A":
            return {"bvps": float(value)}
    return {"bvps": None}


def _valid_numeric_character(x):
    return str.isdigit(x) or x in [".", ","]


# Takes a fetched string number, such as '700M', and converts it to a float
def str_to_num(num_str):
    digits = "".join(filter(_valid_numeric_character, num_str))
    if not digits:
        digits = "0"
    if "T" in num_str:
        return float(locale.atof(digits)) * 1000000000000
    if "B" in num_str:
        return float(locale.atof(digits)) * 1000000000
    if "M" in num_str:
        return float(locale.atof(digits)) * 1000000
    if num_str != "N/A":
        return float(locale.atof(digits))


def yf_quote_search(soup, text):
    found = soup.find("td", {"data-test": text})
    if not found:
        return
    item = found.get_text(strip=True)
    if any(x in ["%", "(", ")"] for x in item):
        return item
    return str_to_num(item)


def _mw_combine_table_dicts(table_dicts):
    combined_dict = {}
    for table_dict in table_dicts:
        for year, values in table_dict.items():
            if year not in combined_dict:
                combined_dict[year] = {}
            for title, value in values.items():
                combined_dict[year][title] = value
    return combined_dict


def mw_raw_tables_to_dict(soup):
    tables = soup.find("div", {"class": "region--primary"}).findAll("table")
    table_dicts = []
    for table in tables:
        ths = table.find("thead").find("tr").findAll("th")
        column_headers = [x.find("div").get_text(strip=True) for x in ths]
        trs = table.find("tbody").findAll("tr")
        rows = []
        for tr in trs:
            tds = tr.findAll("td")
            rows.append([x.find("div").get_text(strip=True) for x in tds])

        out_dict = {}
        for i in range(len(column_headers)):
            header = column_headers[i]
            out_dict[header] = {}
            for row in rows:
                row_header = row[0]
                try:
                    value = str_to_num(row[i])
                except:
                    value = row[i]

                out_dict[header][row_header] = value

        clean_dict = {}
        for k, v in out_dict.items():
            if re.match(r"\d{4}", k):  # Only take columns which are years
                clean_dict[k] = v

        table_dicts.append(clean_dict)
    return table_dicts


def mw_chart_financials_to_dict(soup):
    tables = soup.find("div", {"class": "region--primary"}).findAll("table")
    table_dicts = []
    for table in tables:
        ths = table.find("thead").find("tr").findAll("th")
        column_headers = [x.find("div").get_text(strip=True) for x in ths]
        trs = table.find("tbody").findAll("tr")
        rows = []
        for tr in trs:
            row_header = tr.find("td").find("div").get_text(strip=True)
            parsed_values = [row_header]

            values = (
                tr.find("div", {"class": "chart--financials"})
                .get("data-chart-data")
                .split(",")
            )
            for value in values:
                if value:
                    parsed_values.append(float(value))
                else:
                    parsed_values.append(0)
            rows.append(parsed_values)

        out_dict = {}
        column_headers = [
            x for x in column_headers if re.match(r"\d{4}", x)
        ]  # Only take columns which are years
        for i in range(len(column_headers)):
            header = column_headers[i]
            out_dict[header] = {}
            for row in rows:
                row_header = row[0]
                value = row[i + 1]
                out_dict[header][row_header] = value

        table_dicts.append(out_dict)
    return table_dicts


def mw_financials_search(soup, text):
    # setup for table based parsing
    # tables = mw_chart_financials_to_dict(soup)
    #  financials = _mw_combine_table_dicts(tables)
    #  years = list(financials.keys())
    #  years.sort()
    #
    #  item = None
    #  items = []
    #
    #  for year in years:
    #      value = financials.get(year, {}).get(text)
    #      items.append(value)
    #      item = value
    #  return {"item" : item, "item_list" : items}

    item_dict = {"item": None, "item_list": None}
    found = soup.find(text=text)

    if found:
        item = None  # Most recent year's value
        item_list = None  # List of 5 previous years' values
        fetch = found.parent.parent.parent.findChildren()
        for elem in fetch:
            elemFound = elem.find("div", {"class": "chart--financials"})
            if elemFound:
                item_list = elemFound.get("data-chart-data").split(",")
                item_list = [float(i) for i in item_list if i != ""]
                if len(item_list) > 0 and item_list[-1] != None:
                    item = float(item_list[-1])
                item_dict.update(item_list=item_list, item=item)
                break
    return item_dict


def mw_profile_search(soup, text):
    item = None
    found = soup.find(text=text)
    if text == "Sector" and found:
        fetch = found.parent.parent.find("span", {"class": "primary"})
        item = fetch.get_text(strip=True)
    elif found:
        fetch = found.parent.parent.find("td", {"class": "w25"})
        if fetch:
            value = fetch.get_text(strip=True)
            if value != "N/A":
                item = float(locale.atof(value))
    return item


# MarketWatch scraper for: 'https://marketwatch.com/investing/stock/symbol/financials'
def scrape_mw_financials(symbol):
    url = f"https://www.marketwatch.com/investing/stock/{symbol.replace('-', '.').lower()}/financials"
    soup = get_soup(url)
    eps_dict = mw_financials_search(soup, "EPS (Basic)")
    sales_dict = mw_financials_search(soup, "Sales/Revenue")
    return {
        "eps": eps_dict.get("item"),
        "eps_list": eps_dict["item_list"],
        "sales": sales_dict["item"],
        "sales_list": sales_dict["item_list"],
    }


# MarketWatch scraper for: 'https://marketwatch.com/investing/stock/symbol/financials/cash-flow'
def scrape_mw_cash_flow(symbol):
    cash_flow_dict = {"dividend": None, "dividend_list": None}
    symbol = symbol.replace("-", ".")  # Convert for URL
    url = (
        "https://www.marketwatch.com/investing/stock/"
        + symbol.lower()
        + "/financials/cash-flow"
    )
    soup = get_soup(url)
    item_dict = mw_financials_search(soup, "Cash Dividends Paid - Total")
    # Marketwatch seems to list all dividends as negative, so adjust values
    if item_dict["item"] != None:
        item_dict["item"] = abs(item_dict["item"])
    if item_dict["item_list"] != None:
        item_dict["item_list"] = [abs(i) for i in item_dict["item_list"]]
    cash_flow_dict.update(dividend=item_dict["item"])
    cash_flow_dict.update(dividend_list=item_dict["item_list"])
    return cash_flow_dict


# MarketWatch scraper for: 'https://marketwatch.com/investing/stock/symbol/financials/balance-sheet'
def scrape_mw_balance_sheet(symbol):
    balance_sheet_dict = {"price": None, "assets": None, "liabilities": None}
    symbol = symbol.replace("-", ".")  # Convert for URL
    url = (
        "https://www.marketwatch.com/investing/stock/"
        + symbol.lower()
        + "/financials/balance-sheet"
    )
    soup = get_soup(url)
    item_dict = mw_financials_search(soup, "Total Assets")
    balance_sheet_dict.update(assets=item_dict["item"])
    item_dict = mw_financials_search(soup, "Total Liabilities")
    balance_sheet_dict.update(liabilities=item_dict["item"])
    # Fetch the price from the top of the page
    price = None
    intraday_price = soup.find("h3", {"class": "intraday__price"})
    if intraday_price:
        price = intraday_price.get_text(strip=True).replace("$", "").replace("€", "")
        if price != None and price != "":
            price = round(float(price), 2)
    balance_sheet_dict.update(price=price)
    return balance_sheet_dict


# MarketWatch scraper for: 'https://marketwatch.com/investing/stock/symbol/company-profile'
def scrape_mw_profile(symbol):
    profile_dict = {
        "curr_ratio": None,
        "pe_ratio": None,
        "pb_ratio": None,
        "sector": None,
    }
    symbol = symbol.replace("-", ".")  # Convert for URL
    url = (
        "https://www.marketwatch.com/investing/stock/"
        + symbol.lower()
        + "/company-profile"
    )
    soup = get_soup(url)
    profile_dict.update(curr_ratio=mw_profile_search(soup, "Current Ratio"))
    # Only overwrites PE ratio if it has a non nonetype value
    pe_ratio = mw_profile_search(soup, "P/E Current")
    if pe_ratio != None:
        profile_dict.update(pe_ratio=pe_ratio)
    profile_dict.update(pbRatio=mw_profile_search(soup, "Price to Book Ratio"))
    profile_dict.update(sector=mw_profile_search(soup, "Sector"))
    return profile_dict


# Finviz scraper for 'https://finviz.com/screener.ashx?v=111&f=fa_curratio_o2,fa_eps5years_pos,fa_epsyoy_pos,fa_pe_low&ft=4':
def scrape_finviz():
    url = "https://finviz.com/screener.ashx?v=111&f=fa_curratio_o2,fa_eps5years_pos,fa_epsyoy_pos,fa_pe_low&ft=4"
    user = password = ""
    f = open("backend/finviz-creds.txt", "r")
    lines = f.read().splitlines()
    if len(lines) > 1:
        user = lines[0]
        password = lines[1]
    f.close()
    print(user)
    print(password)
    soup = get_soup(url, user, password)
    print(soup)
    # TODO - Finish pulling today's matching companies out of this site. Authentication is still not working even with my user/pass.
    return


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
    score = score_summation(
        overall_dict["good_assets"],
        overall_dict["good_curr_ratio"],
        overall_dict["good_dividend"],
        overall_dict["good_eps"],
        overall_dict["good_eps_growth"],
        overall_dict["good_pe_ratio"],
        overall_dict["good_sales"],
    )
    return score


def check(symbol, flags):
    overall_dict, health_result, flags = internal_check(symbol, flags)
    output_handler(overall_dict, health_result, flags)


def internal_check(symbol, flags):
    # Website scraping into a single dict
    # Notes: a. Lists of annual values are ordered from 2015 -> 2019
    #        b. EPS and PE ratio are overwritten by Yahoo nums if also in MW
    overall_dict = {
        "symbol": symbol,
        **scrape_mw_financials(symbol),
        **scrape_mw_balance_sheet(symbol),
        **scrape_mw_profile(symbol),
        **scrape_mw_cash_flow(symbol),
        **scrape_yahoo_quote(symbol),
        **scrape_yahoo_key_stats(symbol),
    }
    overall_dict.update(
        graham_num=alg.graham_num(overall_dict["eps"], overall_dict["bvps"]),
        good_assets=alg.good_assets(
            overall_dict["mkt_cap"], overall_dict["assets"], overall_dict["liabilities"]
        ),
        good_curr_ratio=alg.good_curr_ratio(overall_dict["curr_ratio"]),
        good_dividend=alg.good_dividend(
            overall_dict["dividend"], overall_dict["dividend_list"]
        ),
        good_eps=alg.good_eps(overall_dict["eps_list"]),
        good_eps_growth=alg.good_eps_growth(overall_dict["eps_list"]),
        good_pe_ratio=alg.good_pe_ratio(overall_dict["pe_ratio"]),
        good_sales=alg.good_sales(overall_dict["sales"]),
    )
    score = score_summation(
        overall_dict["good_assets"],
        overall_dict["good_curr_ratio"],
        overall_dict["good_dividend"],
        overall_dict["good_eps"],
        overall_dict["good_eps_growth"],
        overall_dict["good_pe_ratio"],
        overall_dict["good_sales"],
    )
    # TODO - Dividend is the sum of all dividends paid. Divide it by num. shares
    health_result = alg.health_check(
        overall_dict["mkt_cap"],
        overall_dict["sales"],
        overall_dict["pe_ratio"],
        overall_dict["curr_ratio"],
        overall_dict["eps_list"],
        overall_dict["dividend"],
        overall_dict["dividend_list"],
        overall_dict["assets"],
        overall_dict["liabilities"],
    )

    score = total_score(overall_dict)
    overall_dict.update(score=score)
    return overall_dict, health_result, flags


# TODO - Unused at the moment. Refine it, or trash it.
# Gets a red to green color of 13 possibilities based on strength
def gradient_color(strength):
    # Gradient from red (0.0) to green (1.0)
    gradients = [
        "cd5c5c",
        "c1635e",
        "b56b5f",
        "a97261",
        "9d7963",
        "918065",
        "848767",
        "788f68",
        "6c966a",
        "609d6c",
        "54a46e",
        "48ac6f",
        "3cb371",
    ]
    color = "000000"
    offset = 1 / 13  # Offset for each gradient value from 0 to 1
    total = 0.0
    for i in range(0, 12):
        if strength >= total and strength <= (total + offset):
            color = gradients[i]
            return color
        total += offset
    if strength >= 1:
        color = gradients[12]
    elif strength <= 0:
        color = gradients[0]
    return color


# TODO - Get this to work for handling indentation
def reindent(s, num_spaces):
    lines = s.split(s, "\n")
    new_str = ""
    for line in lines:
        new_str += indent(line, num_spaces * " ")
    s = new_str.join("\n")
    # s = indent(line, num_spaces * ' ') for line in lines
    # lines = [(num_spaces * ' ') + s.lstrip(line) for line in s]
    # s = s.join('\n')
    return s


def output_handler(overall_dict, health_result, flags):
    # TODO - Create a text string object, and append everything to it
    symbol = overall_dict["symbol"]
    print("Sector: " + str(overall_dict["sector"]))
    gp_ratio = 0.0
    gp_ratio_color = "red"
    if overall_dict["graham_num"] != None and overall_dict["price"] != None:
        gp_ratio = float(overall_dict["graham_num"] / overall_dict["price"])
        # Color green or red depending on if it's above/below fair value
        if overall_dict["graham_num"] >= overall_dict["price"]:
            gp_ratio_color = "green"
    print(
        "Graham Num/Price: "
        + str(overall_dict["graham_num"])
        + "/"
        + str(overall_dict["price"])
        + " (["
        + gp_ratio_color
        + "]"
        + str(round(gp_ratio, 2))
        + "[/"
        + gp_ratio_color
        + "])"
    )
    print("Dividend Yield: " + str(overall_dict["div_yield"]))
    print("Score: " + str(overall_dict["score"]) + "/7")
    # TODO - Rework strength/weaknesses output
    print(health_result)
    # print(reindent(health_result, 4))

    # Debug flag
    if "d" in flags:
        print("Debug: " + str(overall_dict))
    # Excel update flag
    if "x" in flags:
        excel.update(symbol, overall_dict)
    # Finviz check flag
    if "f" in flags:
        # TODO - Finish implementing a way to fetch this. Auth is needed.
        scrape_finviz()
    return


# Assembles a list of flags passed as arguments
def flag_handler(args):
    flags = []
    for arg in args:
        if arg[:1] == "-":
            for flag in arg[1:]:
                flags.append(flag)
    return flags


def commands(phrase):
    args = phrase.split(" ")
    symbol = str(args[0])
    flags = flag_handler(args)
    check(symbol, flags)
    return
