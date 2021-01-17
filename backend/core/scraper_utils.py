import requests
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
