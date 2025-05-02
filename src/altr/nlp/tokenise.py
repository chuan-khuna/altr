from ..monad.extended_pymonad import Either, Right, Left

import re
from typing import TypeAlias, Callable, List, Union

Text: TypeAlias = str
Token: TypeAlias = str  # token is just a word, in in the LLM context
Word: TypeAlias = str  # human readable word
Tokens: TypeAlias = list[Token]
ErrorMessage: TypeAlias = str


ProcessTokenFunc: TypeAlias = Callable[[Token], Either[ErrorMessage, Token]]
TokeniseFunc: TypeAlias = Callable[[Text], Either[ErrorMessage, Tokens]]
ProcessTextFunc: TypeAlias = Callable[[Text], Either[ErrorMessage, Text]]


def exclude_words(
    words_to_exclude: list[Word],
    tokens: Tokens,
) -> Either[None | ErrorMessage, Tokens]:
    try:
        filtered_tokens = [token for token in tokens if token not in words_to_exclude]
        return Right(filtered_tokens)
    except Exception as e:
        return Left(f"Error excluding words: {e}")


def exclude_by_regex(regex_pattern: str, tokens: Tokens) -> Either[None | ErrorMessage, Tokens]:
    try:
        filtered_tokens = [token for token in tokens if not re.match(regex_pattern, token)]
        return Right(filtered_tokens)
    except Exception as e:
        return Left(f"Error excluding by regex: {e}")


def wrap_text(text: Text):
    return Right(text)


def unwrap_result(maybe: Either[None | ErrorMessage, Tokens]) -> Text | Tokens | None:
    if maybe.is_left():
        print(maybe.error)
        return None
    else:
        return maybe.value


# def pipe(
#     text: Text, *functions: tuple[ProcessTextFunc | TokeniseFunc | ProcessTokenFunc]
# ) -> Either[None | ErrorMessage, Text | Tokens]:
#     result = wrap_text(text)
#     for function in functions:
#         result = result.bind(function)
#     return result


def pipe(
    *functions: tuple[ProcessTextFunc | TokeniseFunc | ProcessTokenFunc],
) -> Callable[[Text], Either[None | ErrorMessage, Text | Tokens]]:
    """
    compose functions together

    Returns: a function that takes an input to be processed with composed functions
    """

    def receive_input(text: Text) -> Either[None | ErrorMessage, Text | Tokens]:
        result = wrap_text(text)
        for function in functions:
            result = result.bind(function)
        return result

    return receive_input


compose = pipe
