import re, locale
from backend.core.scraper_utils import get_soup, expand_num

locale.setlocale(locale.LC_ALL, "en_US.UTF-8")


class YFScraper:
    def __init__(self, symbol):
        self.symbol = symbol
        self.base_url = "https://finance.yahoo.com/quote"

    @property
    def url_symbol(self):
        return self.symbol.lower().replace(".", "-")

    def scrape_quote(self):
        soup = get_soup(f"{self.base_url}/{self.url_symbol}")
        return {
            "div_yield": YFScraper.search_div_yield(soup),
            "eps": YFScraper.quote_search(soup, "EPS_RATIO-value"),
            "mkt_cap": YFScraper.quote_search(soup, "MARKET_CAP-value"),
            "pe_ratio": YFScraper.quote_search(soup, "PE_RATIO-value"),
        }

    def scrape_key_stats(self):
        output_dict = {}
        soup = get_soup(f"{self.base_url}/{self.url_symbol}/key-statistics")
        output_dict["bvps"] = YFScraper.key_stats_search(
            soup, "Book Value Per Share", True
        )
        output_dict["curr_ratio"] = YFScraper.key_stats_search(
            soup, "Current Ratio", True
        )
        output_dict["payout_ratio"] = YFScraper.key_stats_search(
            soup, "Payout Ratio", False
        )
        return output_dict

    @staticmethod
    def key_stats_search(soup, text, is_num):
        result = None
        found = soup.find(text=text)
        if found:
            # TODO - Currently just grabs the 4th element. Find a better way to nav.
            value = found.parent.parent.parent.findChildren()[3].get_text(strip=True)
            if value != "N/A":
                if is_num:
                    result = float(locale.atof(value))
                else:
                    result = value
        return result

    # Dividend yield HTML has 2 locations for div_yield on Yahoo Finance
    def search_div_yield(soup):
        div_yield = YFScraper.quote_search(soup, "TD_YIELD-value")
        if div_yield == None:
            items = YFScraper.quote_search(soup, "DIVIDEND_AND_YIELD-value")
            if items != None:
                # Separates forward dividend from dividend yield
                items = items.split(" ")
                div_yield = items[1].replace("(", "").replace(")", "")
        return div_yield

    def quote_search(soup, text):
        found = soup.find("td", {"data-test": text})
        if not found:
            return
        item = found.get_text(strip=True)
        if any(x in ["%", "(", ")"] for x in item):
            return item
        return expand_num(item)

    def scrape(self):
        return {
            "scraper": "YFScraper",
            "symbol": self.symbol,
            **self.scrape_key_stats(),
            **self.scrape_quote(),
        }
