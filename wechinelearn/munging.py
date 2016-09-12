#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Useful data processing functions.
"""

from datetime import datetime


def get_dayseconds(dt):
    """Returns the number of seconds behind the most recent midnight.

    For example: ``get_dayseconds(datetime(2016, 9, 12, 1, 2, 3)) => 3723``.
    """
    return dt.hour * 3600 + dt.minute * 60 + dt.second


def get_weekseconds(dt):
    """Returns the number of seconds behind the most recent midnight of a Monday.

    For example: ``get_weekseconds(datetime(2016, 9, 12, 0, 5, 0)) => 300.0``.
    Because 2016-09-12 is a Monday, and 5 minutes is 300 seconds.
    """
    return (dt - datetime(1970, 1, 5)).total_seconds() % 604800


def difference(array, n=1):
    """Return the differentiation of and array. By default it's 1-order.

    For example we have ``array = [a1, a2, ... , a10]``. Then we have
    ``difference(array, 1) => [(a2 - a1), (a3 - a2), ... (a10 - a9)]``
    ``difference(array, 2) => [(a3 - a1), (a4 - a2), ... (a10 - a8)]``

    **If any error is raised, replace it with None**.

    **中文文档**

    差分计算函数。在差分的过程中如果有任何异常出现, 则用None代替。
    """
    if n < 1:
        raise ValueError("n can not be less than 1.")
    if len(array) < (n + 1):
        raise ValueError("array length has to be greater or equal than n + 1")

    diff_array = list()
    for i, j in zip(array[:-n], array[n:]):
        try:
            diff_array.append(j - i)
        except:
            diff_array.append(None)
    return diff_array


#--- Unittest ---
if __name__ == "__main__":
    import pytest

    assert get_dayseconds(datetime(2016, 9, 5, 1, 2, 3)) == 3723
    assert get_weekseconds(datetime(2016, 9, 5)) == 0

    assert difference([1, 2, 3], 2) == [2, ]
    with pytest.raises(Exception):
        difference([3, 2, 1], 3)
