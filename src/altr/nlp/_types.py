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
