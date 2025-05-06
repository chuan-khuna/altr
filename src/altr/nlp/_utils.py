def compose(*functions):
    """
    Composes multiple functions into a single function that applies them in sequence.

    Args:
        *functions: A variable number of functions to compose. Each function
                    should take a single argument and return a value.

    Returns:
        A function that takes a single input and applies the composed functions
        in sequence.

    Example:
        >>> def double(x):
        ...     return x * 2
        >>> def increment(x):
        ...     return x + 1
        >>> composed = compose(double, increment)
        >>> composed(3)
        7
    """

    def take_input(x):
        result = x
        for function in functions:
            result = function(result)
        return result

    return take_input
