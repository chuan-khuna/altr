from typing import TypeAlias, Callable, Union, Any
from ..monad.extended_pymonad import Either

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
# function for Maybe monad must takes a normal value and return a wrapped value
# ie, in Haskell, it would be `func :: a -> Maybe b`
##############################
# function that takes a list of tokens and returns a list of tokens (wrapped)
TokensToWrappedTokens: TypeAlias = Callable[[list[Token]], Either[Nothing, list[Token]]]
# function that takes a string and returns a list of tokens (wrapped)
TextToWrappedTokens: TypeAlias = Callable[[Text], Either[Nothing, list[Token]]]
# function that takes a string and returns a string (wrapped)
TextToWrappedText: TypeAlias = Callable[[Text], Either[Nothing, Text]]
AnyToWrappedAny: TypeAlias = Callable[[Any], Either[Nothing, Any]]
