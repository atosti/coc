import requests, json, webbrowser, locale
from bs4 import BeautifulSoup
from requests.auth import HTTPBasicAuth
from rich import print
from pprint import pprint
import re
from backend.core import alg, excel
from backend.core.mw_scraper import MWScraper


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
    output_dict = {"bvps": None, "payout_ratio": None}
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
            output_dict["bvps"] = float(locale.atof(value))
    find_payout_ratio = soup.find(text="Payout Ratio")
    if find_payout_ratio:
        fetch = find_payout_ratio.parent.parent.parent.findChildren()
        # TODO - Currently just grabs the 4th element. Find a better way to nav.
        elem = fetch[3]
        value = elem.get_text(strip=True)
        if value != "N/A":
            output_dict["payout_ratio"] = value
    return output_dict


def yf_quote_search(soup, text):
    found = soup.find("td", {"data-test": text})
    if not found:
        return
    item = found.get_text(strip=True)
    if any(x in ["%", "(", ")"] for x in item):
        return item
    return alg.str_to_num(item)


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
                    value = alg.str_to_num(row[i])
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
    print(user)  # FIXME - Remove later
    print(password)  # FIXME - Remove later
    soup = get_soup(url, user, password)
    print(soup)  # FIXME - Remove later
    # TODO - Finish pulling today's matching companies out of this site. Authentication is still not working even with my user/pass.
    return


def check(symbol, flags):
    mw_scrape = MWScraper(symbol).scrape()
    yahoo_scrape = {**scrape_yahoo_quote(symbol), **scrape_yahoo_key_stats(symbol)}
    scraped_data = {**mw_scrape, **yahoo_scrape}

    overall_dict, health_result, flags = internal_check(symbol, scraped_data, flags)
    return output_handler(overall_dict, health_result, flags)


def internal_check(symbol, overall_dict, flags):
    # Website scraping into a single dict
    # Notes: a. Lists of annual values are ordered from 2015 -> 2019
    #        b. EPS and PE ratio are overwritten by Yahoo nums if also in MW

    score_assessments = [
        alg.good_assets(
            overall_dict["mkt_cap"], overall_dict["assets"], overall_dict["liabilities"]
        ),
        alg.good_curr_ratio(overall_dict["curr_ratio"]),
        alg.good_dividend(overall_dict["dividend"], overall_dict["dividend_list"]),
        alg.good_eps(overall_dict["eps_list"]),
        alg.good_eps_growth(overall_dict["eps_list"], 5),
        alg.good_pe_ratio(overall_dict["pe_ratio"]),
        alg.good_sales(overall_dict["sales"]),
    ]
    overall_dict["score"] = len([x for x in score_assessments if x])
    overall_dict["graham_num"] = alg.graham_num(
        overall_dict["eps"], overall_dict["bvps"]
    )

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
        overall_dict["div_yield"],
    )
    return overall_dict, health_result, flags


def build_colored_ratio(a, b):
    ratio = 0.0
    ratio_color = "red"
    if a is not None and b is not None:
        ratio = float(a / b)
        if a >= b:
            ratio_color = "green"

    return f"([{ratio_color}]{round(ratio, 2)}[/{ratio_color}])"


def output_handler(overall_dict, health_result, flags):
    json_data = None
    # Silent flag, hides console output
    if "s" not in flags:
        gp_ratio_str = build_colored_ratio(
            overall_dict["graham_num"], overall_dict["price"]
        )
        bp_ratio_str = build_colored_ratio(overall_dict["bvps"], overall_dict["price"])

        outputs = [
            f'Symbol: {overall_dict["symbol"].upper()}',
            f'Sector: {overall_dict["sector"]}',
            f'Graham Num/Price: {overall_dict["graham_num"]}/{overall_dict["price"]} {gp_ratio_str}',
            f'Bvps/Price: {overall_dict["bvps"]}/{overall_dict["price"]} {bp_ratio_str}',
            f'Dividend Yield/Payout Ratio: {overall_dict["div_yield"]} ({overall_dict["payout_ratio"]})',
            f'Score: {overall_dict["score"]}/7',
            f"Analysis:",
        ]
        for x in health_result:
            outputs.append(f'{" " * 4}{x}')
        print("\n".join(outputs))

    # JSON output/generation flag
    if "j" in flags:
        json_data = {overall_dict["symbol"]: overall_dict}
    # Debug flag
    if "d" in flags:
        print("Debug: " + str(overall_dict))
    # Excel update flag
    if "x" in flags:
        excel.update(overall_dict["symbol"], overall_dict)
    # Finviz check flag
    if "f" in flags:
        # TODO - Finish implementing a way to fetch this. Auth is needed.
        scrape_finviz()
    return json_data


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
    flags = flag_handler(args)
    symbols = [x for x in args if x[0] != "-"]

    json_str = {}
    error_symbols = []
    for symbol in symbols:
        symbol_json = {}
        try:
            symbol_json = check(symbol, flags)
        except:
            error_symbols.append(symbol)
            
        if symbol_json:
            json_str.update(symbol_json)
    
    if "j" in flags:
        print(json_str)
    
    if error_symbols:
        print()
        print(f'Unable to process the following symbols:')
        
        for symbol in error_symbols:    
            print(f'${symbol.upper()}')
        print()
        
    return
