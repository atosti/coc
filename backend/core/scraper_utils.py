import requests, locale
from bs4 import BeautifulSoup


def get_soup(url, user="", password=""):
    if user and password:
        page = requests.get(url, auth=(user, password))
    else:
        page = requests.get(url)
    return BeautifulSoup(page.content, "html.parser")


def valid_ticker(symbol):
    return (
        200
        == requests.get(
            f"https://www.marketwatch.com/investing/stock/{symbol}"
        ).status_code
    )


# Extracts the numerical digits from an abbreviated number string
def extract_digits(abbreviated_num_str):
    digits = abbreviated_num_str
    for c in abbreviated_num_str:
        # Removes non-digits and any excess, invalid chars
        if not c.isdigit() and c != "." or c == "+" or c == "¹" or c == "²" or c == "³":
            digits = digits.replace(c, "")
    if abbreviated_num_str[0] == "-":
        digits = "-" + digits
    return digits


# Expands an abbreviated number string (e.g. '82.1M' becomes '82100000')
def expand_num(abbreviated_num_str):
    abbreviations = ["M", "B", "T"]
    multiply = False
    digits = extract_digits(abbreviated_num_str)
    for letter in abbreviations:
        if letter == "M":
            multiplier = 1000
        multiplier *= 1000
        if letter in abbreviated_num_str.upper():
            multiply = True
            break
    if not multiply:
        multiplier = 1
    if abbreviated_num_str == "N/A" or digits.count(".") > 1:
        result = None
    else:
        result = float(locale.atof(digits)) * multiplier
    return result
