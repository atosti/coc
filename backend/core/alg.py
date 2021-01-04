import math, locale

# Inputs: Outstanding num. of shares and share price in USD
def mkt_cap(shares, price):
    return shares * price


def curr_ratio(assets, liabilities):
    return float(assets / liabilities)


def pe_ratio(price, eps):
    return float(price / eps)


# Returns the fair value of a stock. The highest price an investor should pay.
def graham_num(eps, bvps):
    if eps is None or bvps is None:
        return
    product = 22.5 * eps * bvps
    normalized_value = round(math.sqrt(abs(product)), 2)
    if product < 0:
        return -1 * normalized_value
    return normalized_value


def get_digits(num_str):
    negative = False
    if num_str[0] == '-':
        negative = True
    for c in num_str:
        if not c.isdigit() and c != '.' or c == '²' or c == '³' or c == '¹':
            num_str = num_str.replace(c, '')
    if negative:
        num_str = '-' + num_str
    return num_str


# Adds or removes T/B/M for Trillion/Billion/Million numerical abbreviations
def str_to_num(num_str):
    num = None
    digits = get_digits(num_str)
    multiplier = 1
    if num_str[0] == '-':
        multiplier *= -1
    if 'T' in num_str.upper():
        multiplier *= 1000000000000
    elif 'B' in num_str.upper():
        multiplier *= 1000000000
    elif 'M' in num_str.upper():
        multiplier *= 1000000
    if num_str != 'N/A' and digits.count('.') <= 1:
        num = float(locale.atof(digits)) * multiplier
    return num


# Currently scores out of 7 to determine health of a stock.
def health_check(
    mkt_cap,
    sales,
    pe_ratio,
    curr_ratio,
    eps_list,
    dividend,
    dividends,
    assets,
    liabilities,
):
    score = 0
    result = ""
    fails = []
    results = {}

    if not sales:
        sales = 0
    sales_str = "${:,.2f}".format(sales)
    results["sales"] = {
        "success": good_sales(sales),
        "message": f"Sales | {sales_str} of $700M",
    }

    results["pe_ratio"] = {
        "success": good_pe_ratio(pe_ratio),
        "message": f"P/E Ratio | {str(pe_ratio)} > 15.0",
    }

    results["curr_ratio"] = {
        "success": good_curr_ratio(curr_ratio),
        "message": f"Curr Ratio | {str(curr_ratio)} < 2.0",
    }

    deficit_yrs = []
    if eps_list is not None:
        for idx, eps in enumerate(eps_list):
            if eps is None or eps < 0:
                deficit_yrs.append(2015 + idx)
    results["eps"] = {
        "success": good_eps(eps_list),
        "message": f"EPS | {str(deficit_yrs)}",
    }

    results["dividend"] = {
        "success": good_dividend(dividend, dividends),
        "message": "Dividend decreased over last 5 yrs",
    }

    results["eps_growth"] = {
        "success": good_eps_growth(eps_list),
        "message": f"Low EPS Growth | {str(eps_list)}",
    }

    message = "Assets |" + str(mkt_cap) + " !< " + str(None)
    if assets and liabilities and mkt_cap:
        value = (assets - liabilities) * 1.5
        message = "Assets |" + str(mkt_cap) + " !< " + str(value)

    results["assets"] = {
        "success": good_assets(mkt_cap, assets, liabilities),
        "message": message,
    }

    score = 0
    fails = []
    for k, v in results.items():
        if v["success"]:
            score += 1
        else:
            fails.append(v["message"])

    if score < 7:
        result = "Weaknesses: " + str(fails)
    else:
        result = "Passes all criteria!"
    return result


def good_sales(sales):
    return sales and sales >= 700000000


def good_pe_ratio(pe_ratio):
    return pe_ratio != None and pe_ratio < 15 and not math.isnan(pe_ratio)


def good_curr_ratio(curr_ratio):
    return curr_ratio and curr_ratio >= 2.0 and not math.isnan(curr_ratio)


# Checks for earnings deficit
def good_eps(eps_list):
    if eps_list == None or len(eps_list) < 5:
        return False

    for eps in eps_list:
        if eps is None or eps < 0 or math.isnan(eps):
            return False
    return True


# TODO - Needs a list of annual dividend payouts over the last 20 years.
# TODO - Add logic to determine whether a dividend payment was missed
def good_dividend(curr_dividend, dividends):
    # If no dividend is paid, then it passes
    return not curr_dividend or dividends == sorted(dividends)


# TODO - EPS needs to be a list from the last 10 years
def good_eps_growth(eps_list):
    if eps_list is None or not eps_list:
        return False
    prev_eps = eps_list[0]
    eps = eps_list[-1]
    if prev_eps is None or eps is None:
        return False
    if prev_eps == 0:
        return False
    percent_growth = float(eps / prev_eps) - 1.0
    # 2.9% annual growth over 10 years is ~33% total
    # 100, 102.9, 105.884, 108.955, 112.115, 115.366, 118.712, 122.155, 125.697, 129.342, 133.093
    # TODO - Currently using 15% growth, since it's using 5 years of data
    return percent_growth >= 0.15


def good_assets(mkt_cap, assets, liabilities):
    if mkt_cap is None or assets is None or liabilities is None:
        return False
    if mkt_cap < ((assets - liabilities) * 1.5):
        return True
    return False
