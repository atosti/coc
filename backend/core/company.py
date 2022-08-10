from backend.core import alg


class Company:
    def __init__(self, symbol, scraped_data):
        self.symbol = symbol
        self.score = 0
        self.update(scraped_data)
        self._calculate_score()
        self._calculate_graham_num()

    def update(self, scraped_data):
        for key in scraped_data:
            value = scraped_data[key]
            if isinstance(value, str) and value.endswith('%'):
                value = value[:-1]
                value = value.replace(",","")
                value = float(value)
            setattr(self, str(key), value)

    def _calculate_score(self):
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

    def _calculate_graham_num(self):
        self.graham_num = alg.graham_num(self.eps, self.bvps)

    def health_check(self):
        self.health_result = alg.health_check(self)
        return self.health_result
