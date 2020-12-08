import os
import datetime
from backend.core.alg import *
import pytest
from hypothesis import given
import hypothesis.strategies as st
from uuid import uuid4

@given(shares=st.integers(), price=st.integers())
def test_market_cap(shares, price):
  assert mkt_cap(shares, price) == shares * price

@given(eps=st.integers(), bvps=st.integers())
def test_graham_number(eps, bvps):
    result = graham_num(eps, bvps)

    product = 22.5 * eps * bvps
    if product < 0:
        assert result < 0
        assert result == -1 * math.sqrt(abs(product))
    else:
        assert result >= 0
        assert result == math.sqrt(product)

@given(sales=st.integers())
def test_good_sales(sales):
    result = good_sales(sales)
    if sales >= 700000000:
        assert result
    else:
        assert not result

@given(pe_ratio=st.floats())
def test_good_pe_ratio(pe_ratio):
    result = good_pe_ratio(pe_ratio)
    if pe_ratio < 15.0:
        assert result
    else:
        assert not result

@given(curr_ratio=st.floats())
def test_good_curr_ratio(curr_ratio):
    result = good_curr_ratio(curr_ratio)
    if curr_ratio >= 2.0:
        assert result
    else:
        assert not result

@given(eps_list=st.lists(st.floats()))
def test_good_eps(eps_list):
    expected = all(list(map(lambda x: x is not None and x >= 0, eps_list)))
    if len(eps_list) == 0:
        expected = False
    result = good_eps(eps_list)
    assert expected == result