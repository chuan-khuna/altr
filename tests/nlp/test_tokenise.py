from altr.nlp.tokenise import *


text = "This is a test"
tokenised_text = ["This", "is", "a", "test"]


###############
# functions need to be implemented when using this package
# ie your own functions
###############
def _tokenise_by_space(text):
    # suppose we have a function that tokenise text by space
    try:
        return Right(text.split(" "))
    except Exception as e:
        return Left(f"Error tokenising by space: {e}")


def _tokenise_but_fail(text):
    try:
        assert False, "This function is supposed to fail"
    except AssertionError as e:
        return Left(f"test tokenise failed: {e}")


def _exclude_words(words, tokens):
    try:
        return Right([token for token in tokens if token not in words])
    except Exception as e:
        return Left(f"Error excluding words: {e}")


def _unwrap_result(result):
    return result.value if result.is_right() else []


def _lift(text):
    # lift a string to a wrapped string
    return Right(text)


###############
# tests
###############
def test_pipe_function_to_tokenise_text():
    wrapped_text = _lift(text)
    pipe_result = pipe(
        _tokenise_by_space,
    )(wrapped_text)
    assert pipe_result.is_right()
    assert pipe_result.value == tokenised_text
    assert _unwrap_result(pipe_result) == tokenised_text


def test_pipe_function_can_exclude_word():
    wrapped_text = _lift(text)
    pipe_result = pipe(
        _tokenise_by_space,
        (lambda tokens: _exclude_words(["a", "is"], tokens)),
    )(wrapped_text)
    assert pipe_result.is_right()
    assert _unwrap_result(pipe_result) == ["This", "test"]


def test_pipe_when_function_fails():
    wrapped_text = _lift(text)
    pipe_result = pipe(
        _tokenise_but_fail,
    )(wrapped_text)
    assert pipe_result.is_left()
    assert isinstance(pipe_result.error, str)
