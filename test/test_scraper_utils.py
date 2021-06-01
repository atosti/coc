import pytest, sys

sys.path.insert(0, '../')
from backend.core.scraper_utils import *
from hypothesis import given
import hypothesis.strategies as st

abbreviated_num_str_regex = (
    r'[+-]?[\d]+(?:[,]?[\d{3}])*(?:[.]?[\d]+)?[BbMmTt]?$'  # e.g. 12.34M
)


@given(num_str=st.from_regex(abbreviated_num_str_regex))
def test_extract_digits(num_str):
    result = extract_digits(num_str)
    negative = False
    if num_str[0] == '-':
        negative = True
    for c in num_str:
        if not c.isdigit() and c != '.' or c == '¹' or c == '²' or c == '³':
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
    if abbreviated_num_str == 'N/A' or digits.count('.') > 1:
        expected = None
    else:
        expected = float(locale.atof(digits)) * multiplier
    result = expand_num(abbreviated_num_str)
    assert expected == result
