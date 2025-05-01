import pytest

from altr.visualisation import set_style, list_styles


def test_list_styles():
    styles = list_styles()
    assert isinstance(styles, list)


def test_set_available_styles():
    style = list_styles()[0]
    set_style(style)


def test_set_invalid_style():
    invalid_style = "invalid_style"
    with pytest.raises(ValueError):
        set_style(invalid_style)
