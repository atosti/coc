import os, datetime, pytest, math, sys

sys.path.insert(0, "../")
from backend.core.handler import *
from hypothesis import given, settings
import hypothesis.strategies as st
from uuid import uuid4
from pprint import pprint


div_yield_regex = "[0-9]*[.]?[0-9]*[%]?"


def generate_financials_dictionary():
    return st.fixed_dictionaries(
        {
            "eps": st.floats(),  # e.g. 2.32
            "eps_list": st.lists(st.floats(), max_size=20),
            "bvps": st.floats(),  # e.g. 134.80
            "mkt_cap": st.floats(min_value=1000000),
            "assets": st.floats(min_value=10000000),
            "liabilities": st.floats(min_value=10000000),
            "curr_ratio": st.floats(min_value=0, max_value=5),
            "dividend": st.floats(min_value=0, max_value=100),
            "dividend_list": st.lists(
                st.floats(min_value=0, max_value=100), max_size=20
            ),
            "pe_ratio": st.floats(min_value=0, max_value=5),
            "sales": st.floats(min_value=1000000),
            "div_yield": st.from_regex(div_yield_regex),
        }
    )


@given(financials=generate_financials_dictionary())
@settings(max_examples=10000, deadline=None)
def test_scoring_logic(financials):
    overall_dict, health_result, flags = internal_check("CMC", financials, [])
    score = 7

    print("----------")
    # C1: Sales
    if not financials["sales"] or financials["sales"] < 700000000:
        print("Failed C1")
        score -= 1

    # C2: Curr Ratio
    if financials["curr_ratio"] < 2:
        print("Failed C2")
        score -= 1

    # C3: Dividends
    sorted_dividend_list = sorted(financials["dividend_list"])
    valid_dividend = financials["dividend"] >= 0
    if not financials["dividend"]:
        pass  # considered valid
    elif financials["dividend_list"] != sorted_dividend_list:
        print("Failed C3")
        score -= 1

    # C4: EPS Deficit
    if not financials["eps_list"]:
        score -= 1
    elif len(financials["eps_list"]) < 5:
        score -= 1
    else:
        for x in financials["eps_list"]:
            if x is None or x < 0 or math.isnan(x):
                print("Failed C4")
                score -= 1
                break

    # C5: EPS Growth
    if not alg.good_eps_growth(financials["eps_list"], 5):
        print("Failed C5")
        score -= 1

    # C6: Assets
    if financials["mkt_cap"] >= (
        (financials["assets"] - financials["liabilities"]) * 1.5
    ):
        print("Failed C6")
        score -= 1

    # C7: P/E Ratio
    if financials["pe_ratio"] == None:
        print("Failed C7")
        score -= 1
    elif financials["pe_ratio"] >= 15:
        print("Failed C7")
        score -= 1
    elif math.isnan(financials["pe_ratio"]):
        print("Failed C7")
        score -= 1

    assert financials["score"] <= score
