import math, locale

# Globals for large numbers
trillion = 1000000000000
billion = 1000000000
million = 1000000

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


# Currently scores out of 7 to determine health of a stock.
def health_check(
    mkt_cap,
    sales,
    pe_ratio,
    curr_ratio,
    eps_list,
    mw_data_range,
    dividend,
    dividends,
    assets,
    liabilities,
    div_yield,
):
    # Criteria 1: Cheap assets are when Mkt cap < (Assets - Liabilities) * 1.5
    nav_str = "None"
    cheap_assets_ratio = "None"
    if assets and liabilities and mkt_cap:
        nav = (assets - liabilities) * 1.5  # Technically: NetAssetValue * 1.5
        nav_str = abbreviate_num(nav)
        cheap_assets_ratio = str(round(nav / mkt_cap, 2))
    success = good_assets(mkt_cap, assets, liabilities)
    message = (
        f"C1: Expensive Assets. "
        + nav_str
        + " !≥ "
        + abbreviate_num(mkt_cap)
        + " (≈ "
        + cheap_assets_ratio
        + ": 1)"
    )
    if success:
        message = (
            f"C1: Cheap Assets. "
            + nav_str
            + " ≥ "
            + abbreviate_num(mkt_cap)
            + " (≈ "
            + cheap_assets_ratio
            + ": 1)"
        )
    c1 = criteria_message_dict(message, success, "assets")

    # Criteria 2: Is earnings growth averaging +2.9% year over year?
    eps_growth = 0
    years = 5  # Currently hard-coded to analyze last 5 years of data
    if eps_list is not None and len(eps_list) >= years:
        truncated_eps = eps_list  # Truncated eps list of last 'years' many years
        for i in range(0, len(eps_list) - years):
            truncated_eps.pop(0)
        if truncated_eps[0] != 0:
            growth_difference = float(truncated_eps[-1] / truncated_eps[0]) - 1
            eps_growth = round(growth_difference * 100, 2)
            # Applies negative sign when EPS has changed from negative to positive
            if truncated_eps[0] < 0 and truncated_eps[-1] > 0:
                eps_growth *= -1
    avg_growth = avg_eps_growth(eps_list, 5)
    if avg_growth != None:
        avg_growth = round(avg_growth, 2)
    success = good_eps_growth(eps_list, years)
    message = f"C2: Low EPS Growth of {str(eps_growth)}% < 15%"
    message += f"\n\tAvg EPS growth vs. EPS 5 years ago: {str(avg_growth)}%"
    if success:
        message = f"C2: EPS Growth of {str(eps_growth)}% ≥ 15%"
        message += f"\n\tAvg EPS growth vs. EPS 5 years ago: {str(avg_growth)}%"
    c2 = criteria_message_dict(message, success, "eps_growth")

    # Criteria 3: No earnings deficit in last 5 yrs
    deficit_yrs = []
    if eps_list is not None:
        deficit_yrs = [
            mw_data_range[i]
            for i in range(0, len(eps_list))
            if eps_list[i] is None or eps_list[i] < 0
        ]
    success = good_eps(eps_list)
    message = f"C3: EPS Deficit in {str(deficit_yrs)}"
    if success:
        message = f"C3: No EPS Deficit in last 5 years"
    c3 = criteria_message_dict(message, success, "eps")

    # Criteria 4: Is its Current Ratio >= 2.0?
    message = f"C4: Current Ratio of {str(curr_ratio)} !≥ 2.0"
    success = good_curr_ratio(curr_ratio)
    if success:
        message = f"C4: Current Ratio of {str(curr_ratio)} ≥ 2.0"
    c4 = criteria_message_dict(message, success, "curr_ratio")

    # Criteria 5: Is its P/E (Price to earnings) Ratio <= 15?
    success = good_pe_ratio(pe_ratio)
    message = f"C5: P/E Ratio of {str(pe_ratio)} !≤ 15.0"
    if success:
        message = f"C5: P/E Ratio of {str(pe_ratio)} ≤ 15.0"
    c5 = criteria_message_dict(message, success, "pe_ratio")

    # Criteria 6: Are its annual sales >= $700M USD?
    if not sales:
        sales = 0
    sales_str = abbreviate_num(sales)
    sales_ratio = str(round(sales / (700 * million), 2))
    message = f"C6: ${sales_str} of $700M sales (≈ {sales_ratio}: 1)"
    c6 = criteria_message_dict(message, good_sales(sales), "sales")

    # Criteria 7: If it pays a div, no missed/reduced payments in last 5 yrs
    success = good_dividend(dividend, dividends)
    message = f"C7: Dividend missed/decr. last 5 years"
    if success and div_yield and div_yield != "N/A":
        message = f"C7: Dividend steady/incr. last 5 years"
    elif success:
        message = f"C7: Dividend not paid"
    c7 = criteria_message_dict(message, success, "dividend")

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
def good_dividend(curr_dividend, dividends):
    # If no dividend is paid, then it passes
    return not curr_dividend or dividends == sorted(dividends)


# Requires 2.9% annual growth YoY, with a minimum of 5 years of data
# Growth is as follows: 100, 102.9, 105.884, 108.955, 112.115, 115.366, 118.712, 122.155, 125.697, 129.342, 133.093
def good_eps_growth(eps_list, years):
    if eps_list is None or not eps_list or len(eps_list) < years:
        return False
    elif eps_list[0] is None or eps_list[-1] is None or eps_list[0] == 0:
        return False
    expected_growth = 1
    actual_growth = 0
    # Truncate eps_list to the last 'years' many years
    for i in range(0, len(eps_list) - years):
        eps_list.pop(0)
    for i in range(0, years):
        expected_growth += 0.029 * expected_growth
    expected_growth -= 1
    if eps_list[0] != 0:
        actual_growth = float(eps_list[-1] / eps_list[0]) - 1.0
        # Applies negative sign when EPS has changed from negative to positive
        if eps_list[0] < 0 and eps_list[-1] > 0:
            actual_growth *= -1
    return actual_growth >= expected_growth


def good_assets(mkt_cap, assets, liabilities):
    if mkt_cap is None or assets is None or liabilities is None:
        return False
    if mkt_cap < ((assets - liabilities) * 1.5):
        return True
    return False
