from backend.core import alg

class Company:
    def __init__(self, symbol):
        self.symbol = symbol
        self.sector = None
        self.price = None
        self.sales_list = None
        self.score = 0
        self.graham_num = None
        self.bvps = None
        self.mkt_cap = None
        self.sales = None
        self.pe_ratio = None
        self.pb_ratio = None
        self.curr_ratio = None
        self.eps_list = None
        self.eps = None
        self.mw_data_range = None
        self.dividend = None
        self.dividend_list= None
        self.assets = None
        self.liabilities = None
        self.div_yield = None

    def update(self, scraped_data):
        self.scraper = scraped_data["scraper"]
        self.symbol = scraped_data["symbol"]
        self.eps = scraped_data["eps"]
        self.eps_list = scraped_data["eps_list"]
        self.sales = scraped_data["sales"]
        self.sales_list = scraped_data["sales_list"]
        self.mw_data_range = scraped_data["mw_data_range"]
        self.curr_ratio = scraped_data["curr_ratio"]
        self.pe_ratio = scraped_data["pe_ratio"]
        self.pb_ratio = scraped_data["pb_ratio"]
        self.sector = scraped_data["sector"]
        self.price = scraped_data["price"]
        self.assets = scraped_data["assets"]
        self.liabilities = scraped_data["liabilities"]
        self.dividend = scraped_data["dividend"]
        self.dividend_list = scraped_data["dividend_list"]
        self.bvps = scraped_data["bvps"]
        self.payout_ratio = scraped_data["payout_ratio"]  
        self.div_yield = scraped_data["div_yield"]
        self.mkt_cap = scraped_data["mkt_cap"]
    
    def calculate_score(self):
        score_assessments = [
            alg.good_assets(self.mkt_cap, self.assets, self.liabilities),
            alg.good_curr_ratio(self.curr_ratio),
            alg.good_dividend(self.dividend, self.dividend_list),
            alg.good_eps(self.eps_list),
            alg.good_eps_growth(self.eps_list, 5),
            alg.good_pe_ratio(self.pe_ratio),
            alg.good_sales(self.sales),
        ]
        self.score = len([x for x in score_assessments if x])
    
    def calculate_graham_num(self):
        self.graham_num = alg.graham_num(self.eps, self.bvps)

    def health_check(self):
        self.health_result = alg.health_check(
            self.mkt_cap,
            self.sales,
            self.pe_ratio,
            self.curr_ratio,
            self.eps_list,
            self.mw_data_range,
            self.dividend,
            self.dividend_list,
            self.assets,
            self.liabilities,
            self.div_yield,
        )
        return self.health_result

