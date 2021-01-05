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
    if num_str[0] == "-":
        negative = True
    for c in num_str:
        if not c.isdigit() and c != "." or c == "²" or c == "³" or c == "¹":
            num_str = num_str.replace(c, "")
    if negative:
        num_str = "-" + num_str
    return num_str


# Removes T/B/M for Trillion/Billion/Million numerical abbreviations
def str_to_num(num_str):
    num = None
    digits = get_digits(num_str)
    multiplier = 1
    if num_str[0] == "-":
        multiplier *= -1
    if "T" in num_str.upper():
        multiplier *= 1000000000000
    elif "B" in num_str.upper():
        multiplier *= 1000000000
    elif "M" in num_str.upper():
        multiplier *= 1000000
    if num_str != "N/A" and digits.count(".") <= 1:
        num = float(locale.atof(digits)) * multiplier
    return num


# Adds T/B/M for Trillion/Billion/Million numerical abbreviations
def num_to_str(num):
    num_str = "None"
    denominator = 1
    abbrev = ""
    if num != None:
        if num >= 1000000000000:
            denominator *= 1000000000000
            abbrev = "T"
        elif num >= 1000000000:
            denominator *= 1000000000
            abbrev = "B"
        elif num >= 1000000:
            denominator *= 1000000
            abbrev = "M"
        num_str = str(round((num / denominator), 2)) + abbrev
    return num_str


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
    div_yield
):
    results = {}
    # Criteria 1: Sales >= $700M
    if not sales:
        sales = 0
    sales_str = num_to_str(sales)
    results["sales"] = {
        "success": good_sales(sales),
        "message": f"C1: ${sales_str} of $700M sales",
    }
    # Criteria 2: Curr ratio >= 2.0
    cr_success = good_curr_ratio(curr_ratio)
    cr_msg = f"C2: Curr. Ratio of {str(curr_ratio)} < 2.0"
    if cr_success:
        cr_msg = f"C2: Curr. Ratio of {str(curr_ratio)} >= 2.0"
    results["curr_ratio"] = {
        "success": cr_success,
        "message": cr_msg,
    }
    # Criteria 3: If it pays a dividend, no missed/reduced payments in last 5 yrs
    d_success = good_dividend(dividend, dividends)
    d_msg = f"C3: Dividend missed/decreased in last 5yrs"
    if d_success and div_yield and div_yield != "N/A":
        d_msg = f"C3: Dividend steady/increasing over last 5yrs"
    elif d_success:
        d_msg = f"C3: Dividend not paid"
    results["dividend"] = {
        "success": d_success,
        "message": d_msg,
    }
    # Criteria 4: No earnings deficit in last 5 yrs
    deficit_yrs = []
    if eps_list is not None:
        for idx, eps in enumerate(eps_list):
            if eps is None or eps < 0:
                deficit_yrs.append(2015 + idx)
    ed_success = good_eps(eps_list)
    ed_msg = f"C4: EPS Deficit in {str(deficit_yrs)}"
    if ed_success:
        ed_msg = f"C4: No EPS Deficit over last 5 yrs"
    results["eps"] = {
        "success": ed_success,
        "message": ed_msg,
    }
    # TODO - Update the msgs to adjust the 15% to be whatever matches the yrs of data calculated for.
    #      - This requires adjustments to good_eps_growth() first.
    # Criteria 5: Earnings growth >= 33% compared to 5 yrs ago
    eps_growth = 0
    if eps_list is not None and len(eps_list) >= 5:
        eps_list_5yrs = eps_list
        # Truncates list to only contain last 5 yrs of data
        if len(eps_list) > 5:
            for i in range (0, len(eps_list) - 5):
                eps_list_5yrs.pop(0)
        eps_growth = float(eps_list[-1] / eps_list[0]) - 1.0
        eps_growth = round(eps_growth * 100, 2)
    eg_success = good_eps_growth(eps_list)
    eg_msg = f"C5: Low EPS Growth of {str(eps_growth)}% < 15%"
    if eg_success:
        eg_msg = f"C5: EPS Growth of {str(eps_growth)}% >= 15%"
    results["eps_growth"] = {
        "success": eg_success,
        "message": eg_msg,
    }
    # Criteria 6: It has cheap assets where [Mkt cap < (Assets - Liabilities) * 1.5]
    #   Essentially, is the value of all its outstanding shares less than 1.5x the assets leftover after paying all its debts.
    mkt_cap_str = num_to_str(mkt_cap)
    value_str = "None"
    if assets and liabilities and mkt_cap:
        value = (assets - liabilities) * 1.5
        value_str = num_to_str(value)
        # ca_msg = f"C6: Expensive assets " + str(mkt_cap_str) + " !< " + str(value_str)
    ca_success = good_assets(mkt_cap, assets, liabilities)
    ca_msg = f"C6: Expensive assets " + mkt_cap_str + " !< " + value_str
    if ca_success:
        ca_msg = f"C6: Cheap assets " + mkt_cap_str + " < " + value_str
    results["assets"] = {
        "success": ca_success,
        "message": ca_msg,
    }
    # Criteria 7: P/E Ratio <= 15?
    per_success = good_pe_ratio(pe_ratio)
    per_msg = f"C7: P/E Ratio of {str(pe_ratio)} > 15.0"
    if per_success:
        per_msg = f"C7: P/E Ratio of {str(pe_ratio)} <= 15.0"    
    results["pe_ratio"] = {
        "success": per_success,
        "message": per_msg,
    }

    score = 0
    criterion = []
    for k, v in results.items():
        if v["success"]:
            score += 1
            criterion.append("[green]" + v["message"] + "[/green]")
        else:
            criterion.append("[red]" + v["message"] + "[/red]")
    result = "Analysis: " + str(criterion)
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
# TODO - Modify this to handle any length of eps_list, and calculate the relatively appropriate growth for 2.9% annually.
def good_eps_growth(eps_list):
    if eps_list is None or not eps_list:
        return False
    # Note: If passing a list longer than 5 yrs, this will no longer be valid, as 15% is a value relative to 5 yrs.
    prev_eps = eps_list[0]
    eps = eps_list[-1]
    if prev_eps is None or eps is None:
        return False
    if prev_eps == 0:
        return False
    percent_growth = float(eps / prev_eps) - 1.0
    # 2.9% annual growth over 10 years is ~33% total
    # Growth is as follows: 100, 102.9, 105.884, 108.955, 112.115, 115.366, 118.712, 122.155, 125.697, 129.342, 133.093
    # TODO - Currently using 15% growth, since it's using 5 years of data
    return percent_growth >= 0.15


def good_assets(mkt_cap, assets, liabilities):
    if mkt_cap is None or assets is None or liabilities is None:
        return False
    if mkt_cap < ((assets - liabilities) * 1.5):
        return True
    return False
