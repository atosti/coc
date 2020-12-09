import math

# Inputs: Outstanding num. of shares and share price in USD
def mkt_cap(shares, price):
    return shares * price

def curr_ratio(assets, liabilities):
    return float(assets / liabilities)

def pe_ratio(price, eps):
    return float(price / eps)

# Returns the fair value of a stock. The highest price an investor should pay.
def graham_num(eps, bvps):
    if eps == None or bvps == None:
        return None
    product = 22.5 * eps * bvps
    if product < 0:
        return -1 * math.sqrt(abs(product))
    return math.sqrt(product)

# Currently scores out of 7 to determine health of a stock.
def health_check(mkt_cap, sales, pe_ratio, curr_ratio, eps_list, dividend, dividends, assets, liabilities):
    score = 0
    result = ''
    fails = []
    if good_sales(sales):
        score += 1
    else:
        if sales != None:
            fails.append("Low Sales|" + str(round(sales, 2)) + " of $700M")
        else:
            fails.append("Low Sales|" + str(sales) + " of $700M")
    if good_pe_ratio(pe_ratio):
        score += 1
    else:
        fails.append("High P/E Ratio|" + str(pe_ratio) + ' > 15.0')
    if good_curr_ratio(curr_ratio):
        score += 1
    else:
        fails.append("Low Curr Ratio|" + str(curr_ratio) + ' < 2.0')
    if good_eps(eps_list):
        score += 1
    else:
        deficit_yrs = []
        if eps_list is not None:
            for idx, eps in enumerate(eps_list):
                if eps is None or eps < 0:
                    deficit_yrs.append(2015 + idx)
            fails.append("Low EPS|" + str(deficit_yrs))
        else:
            fails.append("Low EPS|" + str(eps_list))
    if good_dividend(dividend, dividends):
        score += 1
    else:
        fails.append("Dividend decreased over last 5 yrs")
    if good_eps_growth(eps_list):
        score += 1
    else:
        if eps_list is not None and eps_list:
            prev_eps = eps_list[0]
            eps = eps_list[-1]
            if prev_eps is None or eps is None:
                percent_growth = None
                fails.append('Low EPS Growth %|' + str(percent_growth) + ' < 15')
            else:
                percent_growth = (float(eps / prev_eps) - 1.0) * 100
                fails.append('Low EPS Growth %|' + str(round(percent_growth,2)) + ' < 15')
        else:
            fails.append('Low EPS Growth %|' + str(eps_list) + ' < 15')
    if good_assets(mkt_cap, assets, liabilities):
        score += 1
    else:
        value = None
        if assets != None and liabilities != None and mkt_cap != None:
            value = (assets - liabilities) * 1.5
            fails.append("Expensive Assets|" + str(mkt_cap) + " !< " + str(value))
        else:
            fails.append("Expensive Assets|" + str(mkt_cap) + " !< " + str(value))
    if score < 7:
        result = "Weaknesses: " + str(fails)
    else:
        result = "Passes all criteria!"
    return result

def good_sales(sales):
    if sales and sales >= 700000000:
        return True
    return False

def good_pe_ratio(pe_ratio):
    if pe_ratio == None or pe_ratio >= 15 or math.isnan(pe_ratio):
        return False
    return True

def good_curr_ratio(curr_ratio):
    if curr_ratio == None or curr_ratio < 2.0 or math.isnan(curr_ratio):
        return False
    return True

# Checks for earnings deficit
def good_eps(eps_list):
    if eps_list == None or len(eps_list) == 0:
        return False
    for eps in eps_list:
        if eps is None or eps < 0 or math.isnan(eps):
            return False
    return True

# TODO - Needs a list of annual dividend payouts over the last 20 years.
# TODO - Add logic to determine whether a dividend payment was missed
def good_dividend(curr_dividend, dividends):
    # If no dividend is paid, then it passes
    if not curr_dividend:
        return True
    # Otherwise, check for decreasing dividends
    max_dividend = 0
    for dividend in dividends:
        if dividend == None:
            return False
        if dividend > max_dividend:
            max_dividend = dividend
        elif dividend < max_dividend:
            return False
    return True

# TODO - EPS needs to be a list from the last 10 years
def good_eps_growth(eps_list):
    if eps_list is None or not eps_list:
        return False
    prev_eps = eps_list[0]
    eps = eps_list[-1]
    if prev_eps is None or eps is None:
        return False
    percent_growth = float(eps / prev_eps) - 1.0
    # 2.9% annual growth over 10 years is ~33% total
    #100, 102.9, 105.884, 108.955, 112.115, 115.366, 118.712, 122.155, 125.697, 129.342, 133.093
    # TODO - Currently using 15% growth, since it's using 5 years of data
    if percent_growth >= 0.15:
        return True
    return False
def good_assets(mkt_cap, assets, liabilities):
    if mkt_cap is None or assets is None or liabilities is None:
        return False
    if mkt_cap < ((assets - liabilities) * 1.5):
        return True
    return False
