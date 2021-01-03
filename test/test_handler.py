import os
import datetime
from backend.core.handler import *
import pytest
from hypothesis import given, settings
import hypothesis.strategies as st
from uuid import uuid4
from pprint import pprint
import math


def generate_financials_dictionary():
    return st.fixed_dictionaries({
        "eps" : st.floats(), #2.32
        "eps_list" : st.lists(st.floats(), max_size=20), 
        "bvps" : st.floats(), #134.80
        "mkt_cap" : st.floats(min_value=1000000),
        "assets" : st.floats(min_value=10000000),
        "liabilities" : st.floats(min_value=10000000),
        "curr_ratio" : st.floats(min_value=0, max_value=5),
        "dividend" : st.floats(min_value=0, max_value=100),
        "dividend_list" : st.lists(st.floats(min_value=0, max_value=100), max_size=20),
        "pe_ratio" : st.floats(min_value=0, max_value=5),
        "sales" : st.floats(min_value=1000000)
    })
    

@given(financials=generate_financials_dictionary())
@settings(max_examples=10000, deadline=None)
def test_scoring_logic(financials):
    overall_dict, health_result, flags = internal_check("CMC", financials, [])
    score = 7
    
    # assets
    if financials["mkt_cap"] >= ((financials['assets'] - financials['liabilities']) * 1.5):
        print('failed market cap')
        score -= 1
    
    if financials["curr_ratio"] < 2:
        print('failed curr ratio')
        score -= 1
    
    sorted_dividend_list = sorted(financials["dividend_list"])
    valid_dividend = financials['dividend'] >= 0
    if not financials['dividend']:
        pass # considered valid
    elif financials["dividend_list"] != sorted_dividend_list:
        print('failed dividend list')
        score -= 1
    
    if not financials["eps_list"]:
        print('failed eps list')
        score -= 1
    elif len(financials["eps_list"]) < 5:
        print('failed eps list')
        score -= 1
    else:    
        for x in financials["eps_list"]:
            if x is None:
                print('failed eps list')
                score -= 1
                break
            if x < 0:
                print('failed eps list')
                score -= 1
                break
            if math.isnan(x):
                print('failed eps list')
                score -= 1
                break

    if len(financials["eps_list"]) >= 2:
        prev_eps = financials["eps_list"][0]
        eps = financials["eps_list"][-1]
        if prev_eps is None or eps is None:
            percent_growth = 0
        if prev_eps == 0:
            percent_growth = 0
        else:    
            percent_growth = float(eps / prev_eps) - 1.0
        
        if percent_growth < 0.15:
            print('failed eps')
            score -= 1
    else:
        print('failed eps')
        score -= 1
    
    if financials["pe_ratio"] == None:
        print('failed pe_ratio')
        score -= 1
    elif financials["pe_ratio"] >= 15:
        print('failed pe_ratio')
        score -= 1
    elif math.isnan(financials["pe_ratio"]):
        print('failed pe_ratio')
        score -= 1
    
    if not financials["sales"]:
        print('failed sales')
        score -= 1
    elif financials["sales"] < 700000000:
        print('failed sales')
        score -= 1

    assert financials["score"] <= score