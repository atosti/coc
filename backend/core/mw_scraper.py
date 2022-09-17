import re, locale

from sqlalchemy import column
from backend.core.scraper_utils import get_soup

locale.setlocale(locale.LC_ALL, "en_US.UTF-8")


class MWScraper:
    def __init__(self, symbol):
        self.symbol = symbol
        self.base_url = "https://www.marketwatch.com/investing/stock"

    @property
    def url_symbol(self):
        return self.symbol.lower().replace("-", ".")

    @staticmethod
    def chart_financials_to_dict(soup):
        table_dicts = []
        tables_found = soup.find("div", {"class": "region--primary"})
        column_headers = []
        if tables_found is not None:
            tables = soup.find("div", {"class": "region--primary"}).findAll("table")
            for table in tables:
                ths_found = ths = table.find("thead")
                if ths_found:
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
                        value = None  # Init to none incase no value exists
                        if len(row) > i + 1:
                            value = row[i + 1]
                        out_dict[header][row_header] = value

                table_dicts.append(out_dict)
        return table_dicts

    @staticmethod
    def combine_table_dicts(table_dicts):
        combined_dict = {}
        for table_dict in table_dicts:
            for year, values in table_dict.items():
                if year not in combined_dict:
                    combined_dict[year] = {}
                for title, value in values.items():
                    combined_dict[year][title] = value
        return combined_dict

    @staticmethod
    def financials_search(soup, text):
        # setup for table based parsing
        tables = MWScraper.chart_financials_to_dict(soup)
        financials = MWScraper.combine_table_dicts(tables)
        years = list(financials.keys())
        years.sort()

        item = None
        items = []

        for year in years:
            value = financials.get(year, {}).get(text)
            items.append(value)
            item = value
        return {
            "item": item,
            "item_list": items,
            "year_list": [int(yr) for yr in years],
        }

    @staticmethod
    def profile_search(soup, text):
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

    def scrape_summary(self):
        soup = get_soup(f"{self.base_url}/{self.url_symbol}/")
        found = soup.find(text="Yield")
        dividend_yield = None
        if found:
            raw_dividend_yield = found.parent.next_sibling.next_sibling.contents[0]
            dividend_yield = raw_dividend_yield[: len(raw_dividend_yield) - 1]
        return {
            "div_yield": dividend_yield,
        }

    def scrape_financials(self):
        soup = get_soup(f"{self.base_url}/{self.url_symbol}/financials")
        eps_dict = MWScraper.financials_search(soup, "EPS (Basic)")
        sales_dict = MWScraper.financials_search(soup, "Sales/Revenue")
        diluted_shares = MWScraper.financials_search(soup, "Diluted Shares Outstanding")
        return {
            "eps": eps_dict.get("item"),
            "eps_list": eps_dict["item_list"],
            "sales": sales_dict["item"],
            "sales_list": sales_dict["item_list"],
            "mw_data_range": eps_dict["year_list"],
            "diluted_shares": diluted_shares.get("item"),
        }

    def scrape_profile(self):
        soup = get_soup(f"{self.base_url}/{self.url_symbol}/company-profile")
        return {
            "curr_ratio": MWScraper.profile_search(soup, "Current Ratio"),
            "pe_ratio": MWScraper.profile_search(soup, "P/E Current"),
            "pb_ratio": MWScraper.profile_search(soup, "Price to Book Ratio"),
            "sector": MWScraper.profile_search(soup, "Sector"),
        }

    def scrape_balance_sheet(self):
        soup = get_soup(f"{self.base_url}/{self.url_symbol}/financials/balance-sheet")

        # Fetch the price from the top of the page
        price = None
        intraday_price = soup.find("h2", {"class": "intraday__price"})
        if intraday_price:
            price = (
                intraday_price.get_text(strip=True).replace("$", "").replace("€", "")
            )
            try:
                price = float(locale.atof(price))
            except:
                price = None
            # TODO - Take the price and convert it a USD value based on country codes
            #   p = British pound?

        total_assets_dict = MWScraper.financials_search(soup, "Total Assets")
        total_liabilities_dict = MWScraper.financials_search(soup, "Total Liabilities")
        return {
            "price": price,
            "assets": total_assets_dict["item"],
            "liabilities": total_liabilities_dict["item"],
        }

    def scrape_cash_flow(self):
        soup = get_soup(f"{self.base_url}/{self.url_symbol}/financials/cash-flow")
        dividend_dict = MWScraper.financials_search(soup, "Cash Dividends Paid - Total")

        # Marketwatch seems to list all dividends as negative, so adjust values
        dividend = None
        if dividend_dict["item"] is not None:
            dividend = abs(dividend_dict["item"])

        dividend_list = None
        if dividend_dict["item_list"] is not None:
            dividend_list = [
                abs(i) if i is not None else i for i in dividend_dict["item_list"]
            ]

        return {"dividend": dividend, "dividend_list": dividend_list}

    def scrape(self):
        return {
            "scraper": "MWScraper",
            "symbol": self.symbol,
            **self.scrape_summary(),
            **self.scrape_financials(),
            **self.scrape_profile(),
            **self.scrape_balance_sheet(),
            **self.scrape_cash_flow(),
        }
