import math

# Inputs: Outstanding num. of shares and share price in USD
def mktCap(shares, price):
    return shares * price
def currRatio(assets, liabilities):
    currRatio = float(assets/liabilities)
    return currRatio
def peRatio(price, eps):
    peRatio = float(price / eps)
    return peRatio
# Returns the fair value of a stock. The highest price an investor should pay.
def grahamNum(eps, bvps):
    grahamNum = None
    product = 22.5 * eps * bvps
    if bvps < 0 or eps < 0:
        grahamNum = -1 * math.sqrt(abs(product))
    else:
        grahamNum = math.sqrt(product)
    return grahamNum
# Currently scores out of 7 to determine health of a stock.
def score(mktCap, sales, peRatio, currRatio, epsList, dividendList, assets, liabilities):
    score = 0
    fails = []
    if goodSales(sales):
        score += 1
    else:
        fails.append("Low Sales|" + str(round(sales, 2)) + " of $700M")
    if goodPeRatio(peRatio):
        score += 1
    else:
        fails.append("High P/E Ratio|" + str(peRatio))
    if goodCurrRatio(currRatio):
        score += 1
    else:
        fails.append("Low Curr Ratio|" + str(currRatio))
    if goodEps(epsList):
        score += 1
    else:
        deficitYrs = []
        if epsList is not None:
            for idx, eps in enumerate(epsList):
                if eps < 0:
                    deficitYrs.append(2015 + idx)
            fails.append("Low EPS|" + str(deficitYrs))
        else:
            fails.append("Low EPS|" + str(epsList))
    # TODO - Properly pass dividends here and check the logic on the method.
    # if goodDividend(dividends):
    #     score += 1
    # else:
    fails.append("<Dividends>")
    if goodEpsGrowth(epsList):
        score += 1
    else:
        if epsList is not None:
            prevEps = epsList[0]
            eps = epsList[-1]
            percentGrowth = float(eps / prevEps) - 1.0
            fails.append("Low EPS Growth %|" + str(round(percentGrowth,2)))
        else:
            fails.append("Low EPS Growth %|" + str(epsList))
    if goodAssets(mktCap, assets, liabilities):
        score += 1
    else:
        value = (assets - liabilities) * 1.5
        fails.append("Expensive Assets|" + str(mktCap) + " !< " + str(value))
    print("Fails because: " + str(fails))
    return score

def goodSales(sales):
    if sales is None:
        return False
    if sales >= 700000000:
        return True
    return False
def goodPeRatio(peRatio):
    if peRatio is None:
        return False
    if peRatio < 15:
        return True
    return False
def goodCurrRatio(currRatio):
    if currRatio is None:
        return False
    if currRatio >= 2.0:
        return True
    return False
# Checks for earnings deficit
def goodEps(epsList):
    if epsList is None:
        return False
    for eps in epsList:
        if eps < 0:
            return False
    return True
# TODO - Needs a list of annual dividend payouts over the last 20 years.
# TODO - Add logic to determine whether a dividend payment was missed
# def goodDividend(dividends):
#     for dividend in dividends:
#         if dividend < 0:
#             return False
#     return True
# TODO - EPS needs to be a list from the last 10 years
def goodEpsGrowth(epsList):
    if epsList is None:
        return False
    prevEps = epsList[0]
    eps = epsList[-1]
    percentGrowth = float(eps / prevEps) - 1.0
    # 2.9% annual growth over 10 years is ~33% total
    #100, 102.9, 105.884, 108.955, 112.115, 115.366, 118.712, 122.155, 125.697, 129.342, 133.093
    # TODO - Currently using 15% growth, since it's using 5 years of data
    if percentGrowth >= 0.15:
        return True
    return False
def goodAssets(mktCap, assets, liabilities):
    if mktCap is None or assets is None or liabilities is None:
        return False
    if mktCap < ((assets - liabilities) * 1.5):
        return True
    return False
