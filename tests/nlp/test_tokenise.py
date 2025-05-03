from altr.nlp.tokenise import *


text = "This is a test"
tokenised_text = ["This", "is", "a", "test"]


def tokenise_by_space(text):
    # suppose we have a function that tokenise text by space
    try:
        return Right(text.split(" "))
    except Exception as e:
        return Left(f"Error tokenising by space: {e}")


def test_pipe_function_to_tokenise_text():
    wrapped_text = Right(text)
    pipe_result = pipe(
        tokenise_by_space,
    )(wrapped_text)
    assert pipe_result.is_right()
    assert pipe_result.value == tokenised_text
    assert unwrap_result(pipe_result) == tokenised_text


def test_pipe_function_can_exclude_word():
    def exclude_words(words, tokens):
        try:
            return Right([token for token in tokens if token not in words])
        except Exception as e:
            return Left(f"Error excluding words: {e}")

    wrapped_text = Right(text)
    pipe_result = pipe(
        tokenise_by_space,
        (lambda tokens: exclude_words(["a", "is"], tokens)),
    )(wrapped_text)
    assert pipe_result.is_right()
    assert unwrap_result(pipe_result) == ["This", "test"]
