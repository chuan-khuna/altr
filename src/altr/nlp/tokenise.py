from ._types import Text, Token, Word
from pymonad.tools import curry
import re


@curry(2)
def exclude_words(words: list[Word], tokens: list[Token]) -> list[Token]:
    return [token for token in tokens if token not in words]


@curry(2)
def exclude_by_regex(regex_pattern: str, tokens: list[Token]) -> list[Token]:
    return [token for token in tokens if not re.match(regex_pattern, token)]
