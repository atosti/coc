import os
import datetime
from backend.redux.alg import *
import pytest
from hypothesis import given
import hypothesis.strategies as st
from uuid import uuid4

@given(shares=st.integers(), price=st.integers())
def test_market_cap(shares, price):
  assert mktCap(shares, price) == shares * price

@given(eps=st.integers(), bvps=st.integers())
def test_graham_number(eps, bvps):
    result = grahamNum(eps, bvps)

    product = 22.5 * eps * bvps
    if product < 0:
        assert result < 0
        assert result == -1 * math.sqrt(abs(product))
    else:
        assert result >= 0
        assert result == math.sqrt(product)

@given(sales=st.integers())
def test_good_sales(sales):
    result = goodSales(sales)
    if sales >= 700000000:
        assert result
    else:
        assert not result

@given(peRatio=st.integers())
def test_good_pe_ratio(peRatio):
    result = goodPeRatio(peRatio)
    if peRatio < 15:
        assert result
    else:
        assert not result
        
@given(curr_ratio=st.floats())
def test_good_curr_ratio(curr_ratio):
    result = goodCurrRatio(curr_ratio)
    if result >= 2.0:
        assert result
    else:
        assert not result

@given(eps_list=st.lists(st.integers()))
def test_good_eps(eps_list):
    expected = all(list(map(lambda x: x is not None and x >= 0, eps_list)))
    result = goodEps(eps_list)
    assert expected == result

@given(current_dividend=st.integers(), dividends=st.integers())
def test_good_dividend(current_dividend, dividends):
    expected = all(list(map(lambda x: x is not None and x >= 0, eps_list)))
    result = goodEps(eps_list)
    assert expected == result 
