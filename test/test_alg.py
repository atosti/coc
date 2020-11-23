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