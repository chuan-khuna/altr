# code is assisted by Copilot
# references:
# - https://github.com/jasondelaat/pymonad/tree/release
# - https://www.adit.io/posts/2013-04-17-functors,_applicatives,_and_monads_in_pictures.html
# heavily inspired by https://www.youtube.com/watch?v=r6_Sg-SQmng&ab_channel=DataRockie

from typing import TypeVar, Callable, Generic

T = TypeVar("T")  # any type T
S = TypeVar("S")  # any type S


class Maybe(Generic[T]):
    def __init__(self, value):
        self.value = value

    def __or__(self, func):
        """
        use `|` as a shorthand for `bind`

        example:
        ```python
        Just(1) | (lambda x: Just(x + 1)) | (lambda x: Just(x + 1))
        ```

        """
        return self.bind(func)

    def __rshift__(self, func):
        """
        use `>>` as a shorthand for `bind`

        example:
        ```python
        Just(1) >> (lambda x: Just(x + 1)) >> (lambda x: Just(x + 1))
        ```
        """
        return self.bind(func)

    def is_nothing(self):
        raise NotImplementedError

    def is_just(self):
        raise NotImplementedError

    def bind(self, func):
        """
        `bind` equivalent to >>= (pronounced bind) in Haskell
        (>>=) :: ma -> (a -> mb) -> mb

        bind takes a function that returns a Maybe
        the function takes the value of type `T` and returns a `Maybe S`

        Args:
            func (_type_): `func :: a -> mb`
        """
        raise NotImplementedError

    def __str__(self):
        raise NotImplementedError


class Just(Maybe):
    def __init__(self, value: T) -> 'Just[T]':
        self.value = value

    def is_nothing(self):
        return False

    def is_just(self):
        return True

    def bind(self, func: Callable[[T], Maybe[S]]) -> Maybe[S]:
        return func(self.value)

    def __str__(self):
        return f"Just {self.value}"

    def __repr__(self) -> str:
        return f"Just {self.value}"


class Nothing(Maybe):
    def __init__(self, err_message: str = None) -> 'Nothing[str]':
        self.error = err_message

    def is_nothing(self):
        return True

    def is_just(self):
        return False

    def bind(self, func: Callable[[T], Maybe[S]]) -> 'Nothing[str]':
        """When the input of `bind` is `Nothing`
        the output is also `Nothing`

        Args:
            func (Callable[[T], Maybe[S]]): _description_

        Returns:
            Nothing[str]: _description_
        """
        # just simply return self, or Nothing(self.error)
        return self

    def __str__(self):
        if self.error is None:
            return "Nothing"
        return f"{self.error}"

    def __repr__(self) -> str:
        if self.error is None:
            return "Nothing"
        return f"{self.error}"
