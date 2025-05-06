def compose(*functions):
    def take_input(x):
        result = x
        for function in functions:
            result = function(result)
        return result

    return take_input
