import os, datetime, pytest, sys
sys.path.insert(0, '../')
from backend.core.alg import *
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


abbreviated_num_str_regex = r"[+-]?[\d]+(?:[,]?[\d{3}])*(?:[.]?[\d]+)?[BbMmTt]?$" # 12.34M


@given(num_str=st.from_regex(abbreviated_num_str_regex))
def test_extract_digits(num_str):
    result = extract_digits(num_str)
    negative = False
    if num_str[0] == "-":
        negative = True
    for c in num_str:
        if not c.isdigit() and c != "." or c == "¹" or c == "²" or c == "³":
            num_str = num_str.replace(c, "")
    if negative:
        num_str = "-" + num_str
    expected = num_str
    assert "," not in result
    assert "B" not in result
    assert "b" not in result
    assert "M" not in result
    assert "m" not in result
    assert "T" not in result
    assert "t" not in result
    assert expected == result


@given(abbreviated_num_str=st.from_regex(abbreviated_num_str_regex))
def test_expand_num(abbreviated_num_str):
    abbreviations = ['M', 'B', 'T']
    multiply = False
    digits = extract_digits(abbreviated_num_str)
    for letter in abbreviations:
        if letter == 'M':
            multiplier = 1000
        multiplier *= 1000
        if letter in abbreviated_num_str.upper():
            multiply = True
            break
    if not multiply:
        multiplier = 1
    if abbreviated_num_str == 'N/A' or digits.count(".") > 1:
        expected = None
    else:
        expected = float(locale.atof(digits)) * multiplier
    result = expand_num(abbreviated_num_str)
    assert expected == result


@given(num=st.floats())
def num_to_str_floats(num):
    result = num_to_str(num)
    assert type(result) is str
