import locale
from rich import print
from pprint import pprint
from backend.core import alg, excel
from backend.core.company import Company
from backend.core.mw_scraper import MWScraper
from backend.core.yf_scraper import YFScraper


locale.setlocale(locale.LC_ALL, "en_US.UTF-8")


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
    # TODO - Yahoo scrape is currently broken. See if Yahoo fixes it later.
    yahoo_scrape = YFScraper(symbol).scrape()
    scraped_dicts = [mw_scrape, yahoo_scrape]
    scraped_data = combine_scrapes(scraped_dicts)
    # Calculates values we can't quite fetch
    if not scraped_data["price"]:
        scraped_data["price"] = 1

    scraped_data["bvps"] = alg.bvps(scraped_data["pb_ratio"], scraped_data["price"])
    scraped_data["mkt_cap"] = alg.mkt_cap(
        mw_scrape["diluted_shares"], mw_scrape["price"]
    )
    company = Company(symbol, scraped_data)
    company.calculate_score()
    company.calculate_graham_num()
    return output_handler(company, company.health_check(), flags)


def build_colored_ratio(a, b):
    ratio = 0.0
    ratio_color = "red"
    if a is not None and b is not None:
        ratio = float(a / b)
        if a >= b:
            ratio_color = "green"
    return f"([{ratio_color}]{round(ratio, 2)}[/{ratio_color}])"


def output_handler(company, health_result, flags):
    json_data = None
    # Silent flag, hides console output
    if "s" not in flags:
        gp_ratio_str = build_colored_ratio(company.graham_num, company.price)
        bp_ratio_str = build_colored_ratio(company.bvps, company.price)
        outputs = [
            f"Symbol: {company.symbol.upper()} ({company.sector})",
            f"Graham Num/Price: {company.graham_num}/{company.price} {gp_ratio_str}",
            f"Bvps/Price: {company.bvps}/{company.price} {bp_ratio_str}",
            f"Dividend Yield/Payout Ratio: {company.div_yield} ({company.payout_ratio})",
            f"Score: {company.score}/7",
            f"Analysis (for {company.mw_data_range[-1]} data):",
        ]
        for x in health_result:
            outputs.append(f'{" " * 4}{x}')
        print("\n".join(outputs))

    # JSON output/generation flag
    if "j" in flags:
        json_data = {company.symbol: company.__dict__}
    # Debug flag
    if "d" in flags:
        print("Debug: " + str(company.__dict__))
    # Excel update flag
    if "x" in flags:
        excel.update(company.symbol, company)
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
