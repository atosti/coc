import requests, json, webbrowser, locale, re
from requests.auth import HTTPBasicAuth
from rich import print
from pprint import pprint
from backend.core import alg, excel
from backend.core.mw_scraper import MWScraper
from backend.core.yf_scraper import YFScraper
from backend.core.scraper_utils import get_soup


locale.setlocale(locale.LC_ALL, "en_US.UTF-8")


# Finviz scraper for 'https://finviz.com/screener.ashx?v=111&f=fa_curratio_o2,fa_eps5years_pos,fa_epsyoy_pos,fa_pe_low&ft=4':
# def scrape_finviz():
#     url = 'https://finviz.com/screener.ashx?v=111&f=fa_curratio_o2,fa_eps5years_pos,fa_epsyoy_pos,fa_pe_low&ft=4'
#     user = password = ''
#     f = open('backend/finviz-creds.txt', 'r')
#     lines = f.read().splitlines()
#     if len(lines) > 1:
#         user = lines[0]
#         password = lines[1]
#     f.close()
#     print(user)  # FIXME - Remove later
#     print(password)  # FIXME - Remove later
#     soup = get_soup(url, user, password)
#     print(soup)  # FIXME - Remove later
#     # TODO - Finish pulling today's matching companies out of this site. Authentication is still not working even with my user/pass.
#     return


# Combines a series of dicts without re-introducing Null values
def combine_scrapes(scraped_dicts_list):
    combined_dict = {}
    if len(scraped_dicts_list) > 0:
        combined_dict = scraped_dicts_list[0]  # Initialize to one of the dicts
        for scraped_dict in scraped_dicts_list:
            for key in scraped_dict:
                if scraped_dict[key] != None or not combined_dict.get(key):
                    combined_dict[key] = scraped_dict[key]
    return combined_dict


def check(symbol, flags):
    mw_scrape = MWScraper(symbol).scrape()
    yahoo_scrape = YFScraper(symbol).scrape()
    scraped_dicts = [mw_scrape, yahoo_scrape]
    scraped_data = combine_scrapes(scraped_dicts)
    overall_dict, health_result, flags = internal_check(scraped_data, flags)
    return output_handler(overall_dict, health_result, flags)


# Website scraping into a single dict
# Notes: a. Lists of annual values are ordered from 2015 -> 2019
#        b. EPS and PE ratio are overwritten by Yahoo nums if also in MW
def internal_check(overall_dict, flags):
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
        overall_dict["mw_data_range"],
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
            f'Symbol: {overall_dict["symbol"].upper()} ({overall_dict["sector"]})',
            f'Graham Num/Price: {overall_dict["graham_num"]}/{overall_dict["price"]} {gp_ratio_str}',
            f'Bvps/Price: {overall_dict["bvps"]}/{overall_dict["price"]} {bp_ratio_str}',
            f'Dividend Yield/Payout Ratio: {overall_dict["div_yield"]} ({overall_dict["payout_ratio"]})',
            f'Score: {overall_dict["score"]}/7',
            f'Analysis (for {overall_dict["mw_data_range"][-1]} data):',
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
    # if 'f' in flags:
    #     # TODO - Finish implementing a way to fetch this. Auth is needed.
    #     scrape_finviz()
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
        print(f"Unable to process the following symbols:")
        for symbol in error_symbols:
            print(f"${symbol.upper()}")
        print()
    return
