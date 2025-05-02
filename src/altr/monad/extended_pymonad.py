from pymonad.either import Either as __pyEither
from typing import Any, Generic, TypeVar


M = TypeVar('M')
S = TypeVar('S')
T = TypeVar('T')


class Either(__pyEither, Generic[M, T]):
    """Extend pymonad Either"""

    def __rshift__(self, func):
        """Use `>>` as a shorthand for `bind`"""
        return self.bind(func)

    def __or__(self, func):
        """Use `|` as a shorthand for `bind`"""
        return self.bind(func)

    def then(self, func):
        """Use `then` as a shorthand for `bind`"""
        return self.bind(func)

    @property
    def error(self) -> str | None:
        """when the instance is a Left, can use `l.error` to get the error message"""
        if self.is_left():
            return self.monoid[0]
        return None


def Left(value: M) -> Either[M, Any]:
    """Creates a value of the first possible type in the Either monad."""
    return Either(None, (value, False))


def Right(value: T) -> Either[Any, T]:
    """Creates a value of the second possible type in the Either monad."""
    return Either(value, (None, True))
