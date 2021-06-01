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
    large_nums = {'T': trillion, 'B': billion, 'M': million}
    abbreviation = ''
    denominator = 1
    if num != None:
        for i in large_nums:
            if abs(num) >= large_nums[i]:
                denominator *= large_nums[i]
                abbreviation = i
                break
        result = str(round((num / denominator), 2)) + abbreviation
    if abbreviation == '':
        result = 'None'
    return result


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
    div_yield,
):
    results = {}
    # Criteria 1: Sales >= $700M
    if not sales:
        sales = 0
    sales_str = abbreviate_num(sales)
    results['sales'] = {
        'success': good_sales(sales),
        'message': f'C1: ${sales_str} of $700M sales',
    }
    # Criteria 2: Curr ratio >= 2.0
    cr_success = good_curr_ratio(curr_ratio)
    cr_msg = f'C2: Curr. Ratio of {str(curr_ratio)} < 2.0'
    if cr_success:
        cr_msg = f'C2: Curr. Ratio of {str(curr_ratio)} ≥ 2.0'
    results['curr_ratio'] = {
        'success': cr_success,
        'message': cr_msg,
    }
    # Criteria 3: If it pays a div, no missed/reduced payments in last 5 yrs
    d_success = good_dividend(dividend, dividends)
    d_msg = f'C3: Dividend missed/decr. last 5yrs'
    if d_success and div_yield and div_yield != 'N/A':
        d_msg = f'C3: Dividend steady/incr. last 5yrs'
    elif d_success:
        d_msg = f'C3: Dividend not paid'
    results['dividend'] = {
        'success': d_success,
        'message': d_msg,
    }
    # Criteria 4: No earnings deficit in last 5 yrs
    deficit_yrs = []
    if eps_list is not None:
        for idx, eps in enumerate(eps_list):
            if eps is None or eps < 0:
                deficit_yrs.append(2015 + idx)
    ed_success = good_eps(eps_list)
    ed_msg = f'C4: EPS Deficit in {str(deficit_yrs)}'
    if ed_success:
        ed_msg = f'C4: No EPS Deficit in last 5 yrs'
    results['eps'] = {
        'success': ed_success,
        'message': ed_msg,
    }
    # Note: Currently hard-coding num_yrs to 5 years.
    # Criteria 5: Earnings growth >= 15% compared to 5 yrs ago
    eps_growth = 0
    if eps_list is not None and len(eps_list) >= 5:
        # Truncates list to only contain last 5 yrs of data
        if len(eps_list) >= 5:
            eps_list_5yrs = eps_list
            for i in range(0, len(eps_list) - 5):
                eps_list_5yrs.pop(0)
            if eps_list_5yrs[0] != 0:
                eps_growth = float(eps_list_5yrs[-1] / eps_list_5yrs[0]) - 1
                eps_growth = round(eps_growth * 100, 2)
    eg_success = good_eps_growth(eps_list, 5)
    eg_msg = f'C5: Low EPS Growth of {str(eps_growth)}% < 15%'
    if eg_success:
        eg_msg = f'C5: EPS Growth of {str(eps_growth)}% ≥ 15%'
    results['eps_growth'] = {
        'success': eg_success,
        'message': eg_msg,
    }
    # Criteria 6: It has cheap assets where [Mkt cap < (Assets - Liabilities) * 1.5]
    #   Essentially, is the value of all its outstanding shares less than 1.5x the assets leftover after paying all its debts.
    mkt_cap_str = abbreviate_num(mkt_cap)
    value_str = 'None'
    c6_ratio = 'None'
    if assets and liabilities and mkt_cap:
        value = (assets - liabilities) * 1.5  # NAV * 1.5
        value_str = abbreviate_num(value)
        c6_ratio = str(round(value / mkt_cap, 2))
    ca_success = good_assets(mkt_cap, assets, liabilities)
    ca_msg = (
        f'C6: Expensive Assets | '
        + value_str
        + ' < '
        + mkt_cap_str
        + ' ('
        + c6_ratio
        + ')'
    )
    if ca_success:
        ca_msg = (
            f'C6: Cheap Assets | '
            + value_str
            + ' ≥ '
            + mkt_cap_str
            + ' ('
            + c6_ratio
            + ')'
        )
    results['assets'] = {
        'success': ca_success,
        'message': ca_msg,
    }
    # Criteria 7: P/E Ratio <= 15?
    per_success = good_pe_ratio(pe_ratio)
    per_msg = f'C7: P/E Ratio of {str(pe_ratio)} > 15.0'
    if per_success:
        per_msg = f'C7: P/E Ratio of {str(pe_ratio)} ≤ 15.0'
    results['pe_ratio'] = {
        'success': per_success,
        'message': per_msg,
    }

    score = 0
    criterion = []
    for k, v in results.items():
        if v['success']:
            score += 1
            criterion.append('[green]' + v['message'] + '[/green]')
        else:
            criterion.append('[red]' + v['message'] + '[/red]')
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
def good_eps_growth(eps_list, num_yrs):
    if eps_list is None or not eps_list or len(eps_list) < num_yrs:
        return False
    elif eps_list[0] is None or eps_list[-1] is None or eps_list[0] == 0:
        return False
    expected_growth = 1
    actual_growth = 0
    # Checks data only in last 'num_yrs' many years
    for i in range(0, len(eps_list) - num_yrs):
        eps_list.pop(0)
    for i in range(0, len(eps_list)):
        expected_growth += 0.029 * expected_growth
    expected_growth -= 1
    if eps_list[0] != 0:
        actual_growth = float(eps_list[-1] / eps_list[0]) - 1.0
    return actual_growth >= expected_growth


def good_assets(mkt_cap, assets, liabilities):
    if mkt_cap is None or assets is None or liabilities is None:
        return False
    if mkt_cap < ((assets - liabilities) * 1.5):
        return True
    return False
