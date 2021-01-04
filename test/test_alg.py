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


@given(
    eps=st.floats(min_value=-10000000, max_value=10000000),
    bvps=st.floats(min_value=-10000000, max_value=10000000),
)
def test_graham_number(eps, bvps):
    result = graham_num(eps, bvps)
    product = 22.5 * eps * bvps
    if product < 0:
        assert result < 0
        assert result == -1 * round(math.sqrt(abs(product)), 2)
    else:
        assert result >= 0
        assert result == round(math.sqrt(product), 2)


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
    if len(eps_list) < 5:
        expected = False
    else:
        expected = all(list(map(lambda x: x is not None and x >= 0, eps_list)))

    if len(eps_list) == 0:
        expected = False
    result = good_eps(eps_list)
    assert expected == result


num_str_regex = r'[+-]?[\d]+(?:[,]?[\d{3}])*(?:[.]?[\d]+)?[BbMmTt]?$' # e.g. 321.98M
@given(num_str=st.from_regex(num_str_regex))
def test_get_digits(num_str):
    result = get_digits(num_str)
    negative = False
    if num_str[0] == '-':
        negative = True
    for c in num_str:
        if not c.isdigit() and c != '.' or c == '²' or c == '³' or c == '¹':
            num_str = num_str.replace(c, '')
    if negative:
        num_str = '-' + num_str
    expected = num_str
    assert ',' not in result
    assert 'B' not in result
    assert 'b' not in result
    assert 'M' not in result
    assert 'm' not in result
    assert 'T' not in result
    assert 't' not in result
    assert expected == result

@given(num_str=st.from_regex(num_str_regex))
def test_str_to_num(num_str):
    result = str_to_num(num_str)
    digits = get_digits(num_str)
    multiplier = 1
    if num_str[0] == '-':
        multiplier *= -1
    if 'T' in num_str.upper():
        multiplier *= 1000000000000
    elif 'B' in num_str.upper():
        multiplier *= 1000000000
    elif 'M' in num_str.upper():
        multiplier *= 1000000
    if num_str != 'N/A' and digits.count('.') <= 1:
        num = float(locale.atof(digits)) * multiplier
    expected = num
    assert expected == result