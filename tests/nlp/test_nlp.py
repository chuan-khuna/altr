from altr.nlp import hello


# def test_deliberately_fail():
#     assert False, "This test is deliberately failing to demonstrate the test suite."


def test_hello_returns_string():
    result = hello()
    assert isinstance(result, str)
