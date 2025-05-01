def test_greet_function():
    from altr import greet

    assert isinstance(greet.hello(), str)
