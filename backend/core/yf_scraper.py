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

    # Dividend yield HTML has 2 locations for div_yield on Yahoo Finance
    def search_div_yield(soup):
        div_yield = YFScraper.search_quote(soup, "TD_YIELD-value")
        if div_yield == None:
            items = YFScraper.search_quote(soup, "DIVIDEND_AND_YIELD-value")
            if items != None:
                # Separates forward dividend from dividend yield
                items = items.split(" ")
                div_yield = items[1].replace("(", "").replace(")", "")
        return div_yield

    def scrape_quote(self):
        soup = get_soup(f"{self.base_url}/{self.url_symbol}")
        return {
            "div_yield": YFScraper.search_div_yield(soup),
            "eps": YFScraper.search_quote(soup, "EPS_RATIO-value"),
            "mkt_cap": YFScraper.search_quote(soup, "MARKET_CAP-value"),
            "pe_ratio": YFScraper.search_quote(soup, "PE_RATIO-value"),
        }

    def scrape_key_stats(self):
        output_dict = {"bvps": None, "payout_ratio": None}
        soup = get_soup(f"{self.base_url}/{self.url_symbol}/key-statistics")
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

    def search_quote(soup, text):
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
