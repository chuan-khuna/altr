from ..monad.extended_pymonad import Either, Right, Left

import re
from typing import TypeAlias, Callable, Union


##############################
# core types
##############################
Text: TypeAlias = str
# token is just a word, but in the LLM context, it might not be a human readable word
Token: TypeAlias = str
Word: TypeAlias = str  # human readable word
# Nothing represents an error or absence of value
Nothing: TypeAlias = Union[str, None]

##############################
# function signatures
##############################
# function that takes a list of tokens and returns a list of tokens
TokensToTokens: TypeAlias = Callable[[list[Token]], Either[Nothing, list[Token]]]
# function that takes a string and returns a list of tokens
TextToTokens: TypeAlias = Callable[[Text], Either[Nothing, list[Token]]]
# function that takes a string and returns a string
TextToText: TypeAlias = Callable[[Text], Either[Nothing, Text]]


def exclude_words(
    words_to_exclude: list[Word],
    tokens: list[Token],
) -> Either[Nothing, list[Token]]:
    try:
        filtered_tokens = [token for token in tokens if token not in words_to_exclude]
        return Right(filtered_tokens)
    except Exception as e:
        return Left(f"Error excluding words: {e}")


def exclude_by_regex(regex_pattern: str, tokens: list[Token]) -> Either[Nothing, list[Token]]:
    try:
        filtered_tokens = [token for token in tokens if not re.match(regex_pattern, token)]
        return Right(filtered_tokens)
    except Exception as e:
        return Left(f"Error excluding by regex: {e}")


def unwrap_result(maybe: Either[Nothing, list[Token]]) -> Text | list[Token] | None:
    if maybe.is_left():
        print(maybe.error)
        return None
    else:
        return maybe.value


def pipe(
    *functions: tuple[TextToText | TextToTokens | TokensToTokens],
) -> Callable[[Text], Either[Nothing, Text | list[Token]]]:
    """
    compose functions together

    each function takes the normal value and return wrapped value

    Returns: a function that takes an input to be processed with composed functions
    """

    def take_input(wrapped_input) -> Either[Nothing, Text | list[Token]]:
        result = wrapped_input
        for function in functions:
            result = result.bind(function)
        return result

    return take_input


# compose as alias for pipe
def compose(*functions):
    return pipe(*functions)
