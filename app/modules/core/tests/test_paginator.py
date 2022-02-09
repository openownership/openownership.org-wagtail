import pytest

from django.test import Client

from django.core import paginator as django_paginator

from modules.core.paginator import DiggPaginator


def test_page_string():
    p = DiggPaginator(range(1, 1000), 10, body=5).page(1)
    assert str(p) == "1 2 3 4 5 ... 99 100"

def test_error_with_string_page_number():
    with pytest.raises(django_paginator.PageNotAnInteger):
        DiggPaginator(range(1, 1000), 10, body=5).page("foo")

def test_error_with_too_high_page_number():
    with pytest.raises(django_paginator.EmptyPage):
        DiggPaginator(range(1, 1000), 10, body=5).page(999)

def test_softlimit():
    p = DiggPaginator(range(1, 1000), 10, body=5).page(999, softlimit=True)
    assert p.number == 100

def test_odd_body_length_1():
    p = DiggPaginator(range(1, 1000), 10, body=5).page(1)
    assert p.number == 1
    assert p.page_range == [1, 2, 3, 4, 5, False, 99, 100]

def test_odd_body_length_100():
    p = DiggPaginator(range(1, 1000), 10, body=5).page(100)
    assert p.number == 100
    assert p.page_range == [1, 2, False, 96, 97, 98, 99, 100]

def test_even_body_length_1():
    p = DiggPaginator(range(1, 1000), 10, body=6).page(1)
    assert p.number == 1
    assert p.page_range == [1, 2, 3, 4, 5, 6, False, 99, 100]

def test_even_body_length_100():
    p = DiggPaginator(range(1, 1000), 10, body=6).page(100)
    assert p.number == 100
    assert p.page_range == [1, 2, False, 95, 96, 97, 98, 99, 100]

def test_combine_leading_range_1():
    p = DiggPaginator(range(1, 1000), 10, body=5, padding=2, margin=2).page(3)
    assert p.number == 3
    assert p.page_range == [1, 2, 3, 4, 5, False, 99, 100]

def test_combine_leading_range_2():
    p = DiggPaginator(range(1, 1000), 10, body=6, padding=2, margin=2).page(4)
    assert p.number == 4
    assert p.page_range == [1, 2, 3, 4, 5, 6, False, 99, 100]

def test_combine_leading_range_3():
    p = DiggPaginator(range(1, 1000), 10, body=5, padding=1, margin=2).page(6)
    assert p.number == 6
    assert p.page_range == [1, 2, 3, 4, 5, 6, 7, False, 99, 100]

def test_combine_leading_range_4():
    p = DiggPaginator(range(1, 1000), 10, body=5, padding=2, margin=2).page(7)
    assert p.number == 7
    assert p.page_range == [1, 2, False, 5, 6, 7, 8, 9, False, 99, 100]

def test_combine_leading_range_5():
    p = DiggPaginator(range(1, 1000), 10, body=5, padding=1, margin=2).page(7)
    assert p.number == 7
    assert p.page_range == [1, 2, False, 5, 6, 7, 8, 9, False, 99, 100]

def test_combine_trailing_range_1():
    p = DiggPaginator(range(1, 1000), 10, body=5, padding=2, margin=2).page(98)
    assert p.number == 98
    assert p.page_range == [1, 2, False, 96, 97, 98, 99, 100]

def test_combine_trailing_range_2():
    p = DiggPaginator(range(1, 1000), 10, body=6, padding=2, margin=2).page(97)
    assert p.number == 97
    assert p.page_range == [1, 2, False, 95, 96, 97, 98, 99, 100]

def test_combine_trailing_range_3():
    p = DiggPaginator(range(1, 1000), 10, body=5, padding=1, margin=2).page(95)
    assert p.number == 95
    assert p.page_range == [1, 2, False, 94, 95, 96, 97, 98, 99, 100]

def test_combine_trailing_range_4():
    p = DiggPaginator(range(1, 1000), 10, body=5, padding=2, margin=2).page(94)
    assert p.number == 94
    assert p.page_range == [1, 2, False, 92, 93, 94, 95, 96, False, 99, 100]

def test_combine_trailing_range_5():
    p = DiggPaginator(range(1, 1000), 10, body=5, padding=1, margin=2).page(94)
    assert p.number == 94
    assert p.page_range == [1, 2, False, 92, 93, 94, 95, 96, False, 99, 100]

def test_combine_all_ranges_1():
    p = DiggPaginator(range(1, 151), 10, body=6, padding=2).page(7)
    assert p.number == 7
    assert p.page_range == [1, 2, 3, 4, 5, 6, 7, 8, 9, False, 14, 15]

def test_combine_all_ranges_2():
    p = DiggPaginator(range(1, 151), 10, body=6, padding=2).page(8)
    assert p.number == 8
    assert p.page_range == [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15]

def test_combine_all_ranges_3():
    p = DiggPaginator(range(1, 151), 10, body=6, padding=1).page(8)
    assert p.number == 8
    assert p.page_range == [1, 2, 3, 4, 5, 6, 7, 8, 9, False, 14, 15]

def test_no_leading_or_trainling_ranges_1():
    p = DiggPaginator(range(1, 80), 10, body=10).page(1)
    assert p.number == 1
    assert p.page_range == [1, 2, 3, 4, 5, 6, 7, 8]

def test_no_leading_or_trainling_ranges_2():
    p = DiggPaginator(range(1, 80), 10, body=10).page(8)
    assert p.number == 8
    assert p.page_range == [1, 2, 3, 4, 5, 6, 7, 8]

def test_no_leading_or_trainling_ranges_3():
    p = DiggPaginator(range(1, 12), 10, body=5).page(1)
    assert p.number == 1
    assert p.page_range == [1, 2]

def test_left_align_mode_1():
    p = DiggPaginator(range(1, 1000), 10, body=5, align_left=True).page(1)
    assert p.number == 1
    assert p.page_range == [1, 2, 3, 4, 5]

def test_left_align_mode_2():
    p = DiggPaginator(range(1, 1000), 10, body=5, align_left=True).page(50)
    assert p.number == 50
    assert p.page_range == [1, 2, False, 48, 49, 50, 51, 52]

def test_left_align_mode_3():
    p = DiggPaginator(range(1, 1000), 10, body=5, align_left=True).page(97)
    assert p.number == 97
    assert p.page_range == [1, 2, False, 95, 96, 97, 98, 99]

def test_left_align_mode_4():
    p = DiggPaginator(range(1, 1000), 10, body=5, align_left=True).page(100)
    assert p.number == 100
    assert p.page_range == [1, 2, False, 96, 97, 98, 99, 100]

def test_default_padding():
    assert 4 == DiggPaginator(range(1, 1000), 10, body=10).padding

def test_automatic_padding_reduction_1():
    assert 2 == DiggPaginator(range(1, 1000), 10, body=5).padding

def test_automatic_padding_reduction_2():
    assert 2 == DiggPaginator(range(1, 1000), 10, body=6).padding

def test_padding_sanity_check():
    with pytest.raises(ValueError):
        DiggPaginator(range(1, 1000), 10, body=5, padding=3)
