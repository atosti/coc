# Inputs: Outstanding num. of shares and share price in USD
def mktCap(shares, price):
    return shares * price
def currRatio(assets, liabilities):
    currRatio = float(assets/liabilities)
    return currRatio
def peRatio(price, eps):
    peRatio = float(price / eps)
    return peRatio
# Currently scores out of 7 to determine health of a stock.
def score(mktCap, peRatio, currRatio, epsList, dividends, assets, liabilities):
    score = 0
    fails = []
    if goodMktCap(mktCap):
        score += 1
    else:
        fails.append("Mkt. Cap")   
    if goodPeRatio(peRatio):
        score += 1
    else:
        fails.append("P/E Ratio")
    if goodCurrRatio(currRatio):
        score += 1
    else:
        fails.append("Curr Ratio")
    if goodEps(epsList):
        score += 1
    else:
        fails.append("EPS")
    # TODO - Properly pass dividends here and check the logic on the method.
    # if goodDividend(dividends):
    #     score += 1
    # else:
    fails.append("<Dividends>")
    if goodEpsGrowth(epsList):
        score += 1
    else:
        fails.append("EPS Growth")
    if goodAssets(mktCap, assets, liabilities):
        score += 1
    else:
        fails.append("Assets")
    print("Fails on: " + str(fails))
    return score
# Inputs: Market cap in USD
def goodMktCap(mktCap):
    if mktCap >= 700000000:
        return True
    return False
# Inputs: Share price and earnings per share
def goodPeRatio(peRatio):
    if peRatio < 15:
        return True
    return False
def goodCurrRatio(currRatio):
    if currRatio >= 2.0:
        return True
    return False
# TODO - Needs a list of annual EPS over the last 10 years.
def goodEps(epsList):
    for eps in epsList:
        if eps < 0:
            return False
    return True
# TODO - Needs a list of annual dividend payouts over the last 20 years.
def goodDividend(dividends):
    for dividend in dividends:
        if dividend < 0:
            return False
    return True
# TODO - EPS needs to be a list from the last 10 years
def goodEpsGrowth(epsList):
    prevEps = epsList[0]
    eps = epsList[-1]
    avgEps = float(prevEps / eps) * 100
    if avgEps >= 33.0:
        return True
    return False
def goodAssets(mktCap, assets, liabilities):
    if mktCap < ((assets - liabilities) * 1.5):
        return True
    return False
