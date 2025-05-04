from ..monad.extended_pymonad import Right, Left, Either
from ._types import (
    Word,
    Token,
    Nothing,
    Text,
    TokensToWrappedTokens,
    TextToWrappedTokens,
    TextToWrappedText,
    AnyToWrappedAny,
)
from typing import Callable, TypeAlias

import re

WrappedValue: TypeAlias = Either[Nothing, Text | list[Token]]


def exclude_words(
    words_to_exclude: list[Word],
    tokens: list[Token],
) -> Either[Nothing, list[Token]]:
    """Exclude words from the list of tokens"""
    try:
        filtered_tokens = [token for token in tokens if token not in words_to_exclude]
        return Right(filtered_tokens)
    except Exception as e:
        return Left(f"Error excluding words: {e}")


def exclude_by_regex(regex_pattern: str, tokens: list[Token]) -> Either[Nothing, list[Token]]:
    """Exclude tokens that match the regex pattern"""
    try:
        filtered_tokens = [token for token in tokens if not re.match(regex_pattern, token)]
        return Right(filtered_tokens)
    except Exception as e:
        return Left(f"Error excluding by regex: {e}")


def pipe(
    *functions: tuple[TextToWrappedText | TextToWrappedTokens | TokensToWrappedTokens | AnyToWrappedAny],
) -> Callable[[WrappedValue], WrappedValue]:
    """
    Compose functions together
    each function takes the normal value and return wrapped value

    Returns: a composed function that takes a wrapped input to be processed with composed functions
    """

    def take_input(wrapped_input: WrappedValue) -> WrappedValue:
        result = wrapped_input
        for function in functions:
            result = result.bind(function)
        return result

    return take_input


# compose as alias for pipe
compose = pipe
