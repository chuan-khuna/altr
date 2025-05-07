from ._types import Token
from ._utils import compose

from copy import deepcopy
from typing import Callable


def prepare_data_for_ngram(
    tokenised_texts: list[list[Token]],
) -> tuple[dict[int, object | None], dict[int, list[list[Token]]], dict[int, list[list[Token]]]]:
    """Initialise ngram processing structures.

    Returns:
        - models dict (initially `{1: None}`)
        - ngram tokens dict (initially `{1: list of tokenised texts}`)
        - filtered ngram tokens dict, this store only n-gram tokens (initially `{1: list of tokenised texts}`)
    """
    return ({1: None}, {1: tokenised_texts}, {1: tokenised_texts})


def process_ngram(
    training_model_fn: Callable[[list[list[Token]]], object],
    get_ngram_tokens_fn: Callable[[object, list[list[Token]]], list[list[Token]]],
    filter_ngram_tokens_fn: Callable[[list[list[Token]]], list[list[Token]]],
    concat_ngram_tokens_fn: Callable[[list[list[Token]]], list[list[Token]]],
) -> Callable[
    [tuple[dict[int, object | None], dict[int, list[list[Token]]], dict[int, list[list[Token]]]]],
    tuple[dict[int, object | None], dict[int, list[list[Token]]], dict[int, list[list[Token]]]],
]:
    """
    Creates a pipeline to process n-gram tokens.

    Args:
        training_model_fn (Callable): Trains a model using a list of tokenized texts.
        get_ngram_tokens_fn (Callable): Generates n-gram tokens using a model and tokenized texts.
        filter_ngram_tokens_fn (Callable): Filters n-gram tokens from the input.
        concat_ngram_tokens_fn (Callable): Concatenates n-gram tokens by removing delimiters.

    Returns:
        Callable: A function that processes n-gram tokens and updates the input data structures.
    """

    filter_ngram_pipeline = compose(filter_ngram_tokens_fn, concat_ngram_tokens_fn)

    def process(
        input_tuple: tuple[dict[int, object | None], dict[int, list[list[Token]]], dict[int, list[list[Token]]]],
    ) -> tuple[dict[int, object | None], dict[int, list[list[Token]]], dict[int, list[list[Token]]]]:
        # extract data from input tuple
        models, ngram_tokens, ngram_tokens_filtered = input_tuple

        # find the previous number of ngram
        max_ngram = max(models.keys())
        next_ngram = max_ngram + 1
        model_input = ngram_tokens[max_ngram]

        model = training_model_fn(model_input)
        ngram_result = get_ngram_tokens_fn(model, model_input)

        # filter only ngram tokens
        ngram_result_filtered = filter_ngram_pipeline(ngram_result)
        ngram_result = concat_ngram_tokens_fn(ngram_result)

        # return new dicts, avoid mutation
        new_models = deepcopy(models)
        new_tokens = deepcopy(ngram_tokens)
        new_filtered = deepcopy(ngram_tokens_filtered)

        new_models[next_ngram] = model
        new_tokens[next_ngram] = ngram_result
        new_filtered[next_ngram] = ngram_result_filtered

        return new_models, new_tokens, new_filtered

    return process
