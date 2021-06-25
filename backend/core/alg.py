import math, locale

# Constants for referencing very large numbers
trillion = 1000000000000
billion = 1000000000
million = 1000000

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


# Creates an abbreviated num str from a number (e.g. 64150000 becomes '64.15M')
def abbreviate_num(num):
    large_nums = {"T": trillion, "B": billion, "M": million}
    abbreviation = ""
    denominator = 1
    if num != None:
        for i in large_nums:
            if abs(num) >= large_nums[i]:
                denominator *= large_nums[i]
                abbreviation = i
                break
        result = str(round((num / denominator), 2)) + abbreviation
    if abbreviation == "":
        result = "None"
    return result


# TODO - Determine if this is actually that helpful. If so, describe it better.
# Returns avg. EPS vs initial EPS of the period (in years) as a percentage
def avg_eps_growth(eps_list, period):
    avg_percent = None
    truncated_eps = eps_list  # Truncated eps list of only years in the period
    for i in range(0, len(eps_list) - period):
        truncated_eps.pop(0)
    if len(truncated_eps) > 0 and truncated_eps[0] != 0:
        avg_growth = sum(truncated_eps) / len(truncated_eps)
        # Must handle double negatives differently to preserve accuracy
        if avg_growth < 0 and truncated_eps[0] < 0:
            growth_difference = float(avg_growth / truncated_eps[0]) * -1
            growth_difference += 1
        else:
            growth_difference = float(avg_growth / truncated_eps[0]) - 1
        avg_percent = growth_difference * 100
    return avg_percent


# Assembles a criteria message into a dict
def criteria_message_dict(criteria_message, strength, key):
    results = {}
    results[key] = {
        "success": strength,
        "message": criteria_message,
    }
    return results


def calculate_rounded_ratio(num_a, num_b, digits):
    return str(round(num_a / num_b, digits))


def eps_growth(eps_list, years):
    eps_growth = None
    if eps_list is None or not eps_list or len(eps_list) < years:
        return eps_growth
    elif eps_list[0] is None or eps_list[-1] is None or eps_list[0] == 0:
        return eps_growth
    truncated_eps_list = truncate_eps_list(eps_list, years)
    if truncated_eps_list[0] != 0:
        eps_growth = float(truncated_eps_list[-1] / truncated_eps_list[0]) - 1.0
        # Applies negative sign when EPS has changed from negative to positive
        if truncated_eps_list[0] < 0 and truncated_eps_list[-1] > 0:
            eps_growth *= -1
    return eps_growth


def net_asset_value(assets, liabilities):
    nav = 0
    if assets and liabilities:
        nav = assets - liabilities
    return nav


# Criteria 1: Cheap assets are when MktCap < (Assets - Liabilities) * 1.5
def criteria_one(mkt_cap, assets, liabilities):
    nav_str = "None"
    cheap_assets_ratio = "None"
    if mkt_cap:
        nav = net_asset_value(assets, liabilities)
        nav_str = abbreviate_num(nav * 1.5)
        cheap_assets_ratio = calculate_rounded_ratio(nav * 1.5, mkt_cap, 2)
    success = good_assets(mkt_cap, assets, liabilities)
    message = (f"C1: Expensive Assets. {nav_str} !≥ {abbreviate_num(mkt_cap)}"
        + f" (≈ {cheap_assets_ratio}: 1)"
    )
    if success:
        message = (
            f"C1: Cheap Assets. {nav_str} ≥ {abbreviate_num(mkt_cap)}"
            + f" (≈ {cheap_assets_ratio}: 1)"
        )
    return criteria_message_dict(message, success, "assets")


# Criteria 2: Is earnings growth averaging +2.9% year over year?
def criteria_two(eps_list):
    years = 5  # Currently hard-coded to analyze last 5 years of data
    actual_growth = eps_growth(eps_list, years)
    # TODO - Decide if you actually want the avg_growth metric. It's confusing.
    # avg_growth = avg_eps_growth(eps_list, 5)
    # if avg_growth != None:
        # avg_growth = round(avg_growth, 2)
    success = good_eps_growth(eps_list, years)
    message = f"C2: Low EPS Growth of {str(round(actual_growth * 100, 2))}% < 15%"
    # message += f"\n\tAvg EPS growth vs. EPS 5 years ago: {str(avg_growth)}%"
    if success:
        message = f"C2: EPS Growth of {str(round(actual_growth * 100, 2))}% ≥ 15%"
        # message += f"\n\tAvg EPS growth vs. EPS 5 years ago: {str(avg_growth)}%"
    return criteria_message_dict(message, success, "eps_growth")


def calculate_eps_deficit_years(eps_list, mw_data_range):
    deficit_yrs = []
    if eps_list is not None:
        deficit_yrs = [
            mw_data_range[i]
            for i in range(0, len(eps_list))
            if eps_list[i] is None or eps_list[i] < 0
        ]
    return deficit_yrs


# Criteria 3: No earnings deficit in last 5 yrs
def criteria_three(eps_list, mw_data_range):
    deficit_yrs = calculate_eps_deficit_years(eps_list, mw_data_range)
    success = good_eps(eps_list)
    message = f"C3: EPS Deficit in {str(deficit_yrs)}"
    if success:
        message = f"C3: No EPS Deficit in last 5 years"
    return criteria_message_dict(message, success, "eps")


# Criteria 4: Is its Current Ratio >= 2.0?
def criteria_four(curr_ratio):
    message = f"C4: Current Ratio of {str(curr_ratio)} !≥ 2.0"
    success = good_curr_ratio(curr_ratio)
    if success:
        message = f"C4: Current Ratio of {str(curr_ratio)} ≥ 2.0"
    return criteria_message_dict(message, success, "curr_ratio")


# Criteria 5: Is its P/E (Price to earnings) Ratio <= 15?
def criteria_five(pe_ratio):
    success = good_pe_ratio(pe_ratio)
    message = f"C5: P/E Ratio of {str(pe_ratio)} !≤ 15.0"
    if success:
        message = f"C5: P/E Ratio of {str(pe_ratio)} ≤ 15.0"
    return criteria_message_dict(message, success, "pe_ratio")


# Criteria 6: Are its annual sales >= $700M USD?
def criteria_six(sales):
    if not sales:
        sales = 0
    sales_str = abbreviate_num(sales)
    sales_ratio = calculate_rounded_ratio(sales, 700 * million, 2)
    message = f"C6: ${sales_str} of $700M sales (≈ {sales_ratio}: 1)"
    return criteria_message_dict(message, good_sales(sales), "sales")


# Criteria 7: If it pays a div, no missed/reduced payments in last 5 yrs
def criteria_seven(dividend, dividend_list, div_yield):
    success = good_dividend(dividend, dividend_list)
    message = f"C7: Dividend missed/decr. last 5 years"
    if success and div_yield and div_yield != "N/A":
        message = f"C7: Dividend steady/incr. last 5 years"
    elif success:
        message = f"C7: Dividend not paid"
    return criteria_message_dict(message, success, "dividend")


# Currently scores out of 7 to determine health of a stock.
def health_check(company):
    c1 = criteria_one(company.mkt_cap, company.assets, company.liabilities)
    c2 = criteria_two(company.eps_list)
    c3 = criteria_three(company.eps_list, company.mw_data_range)
    c4 = criteria_four(company.curr_ratio)
    c5 = criteria_five(company.pe_ratio)
    c6 = criteria_six(company.sales)
    c7 = criteria_seven(company.dividend, company.dividend_list,
        company.div_yield
    )
    criteria_messages = {**c1, **c2, **c3, **c4, **c5, **c6, **c7}
    # Colors the criteria output
    criterion = []
    for k, v in criteria_messages.items():
        if v["success"]:
            if "Dividend not paid" in v["message"]:
                criterion.append("[yellow]" + v["message"] + "[/yellow]")
            else:
                criterion.append("[green]" + v["message"] + "[/green]")
        else:
            criterion.append("[red]" + v["message"] + "[/red]")
    result = criterion
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
def good_dividend(curr_dividend, dividend_list):
    # If no dividend is paid, then it passes
    return not curr_dividend or dividend_list == sorted(dividend_list)


# Truncates the EPS list into the most recent X many years
def truncate_eps_list(eps_list, years):
    for i in range(0, len(eps_list) - years):
        eps_list.pop(0)
    return eps_list


# Determines expected EPS growth in a period, given expectations of +2.9%/year
def expected_eps_growth(years):
    expected_growth = 1
    for i in range(0, years):
        expected_growth += 0.029 * expected_growth
    expected_growth -= 1
    return expected_growth


# Defined as at least 2.9% annual growth YoY for the period
def good_eps_growth(eps_list, years):
    if eps_list is None or not eps_list or len(eps_list) < years:
        return False
    elif eps_list[0] is None or eps_list[-1] is None or eps_list[0] == 0:
        return False
    expected_growth = expected_eps_growth(years)
    actual_growth = eps_growth(eps_list, years)
    return actual_growth >= expected_growth


def good_assets(mkt_cap, assets, liabilities):
    if mkt_cap is None or assets is None or liabilities is None:
        return False
    if mkt_cap < ((assets - liabilities) * 1.5):
        return True
    return False
