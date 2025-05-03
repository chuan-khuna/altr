import pytest

from altr.visualisation import set_style, available_styles
# from altr.visualization import set_style, available_styles
# from altr.vis import set_style, available_styles



def test_get_available_styles():
    assert isinstance(available_styles, list)


def test_set_invalid_style():
    invalid_style = "invalid_style"
    with pytest.raises(Exception):
        set_style(invalid_style)
