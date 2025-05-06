from ._types import Token
from ._utils import compose

from copy import deepcopy

NGRAM_DELIMITER = "<DELIM>"


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


def _filter_only_ngram_tokens(tokenised_texts: list[list[Token]]) -> list[list[Token]]:
    return [[token for token in tokens if NGRAM_DELIMITER in token] for tokens in tokenised_texts]


def _concat_ngram_tokens(tokenised_texts: list[list[Token]]) -> list[list[Token]]:
    return [[token.replace(NGRAM_DELIMITER, "") for token in tokens] for tokens in tokenised_texts]


def process_ngram(training_model_fn, get_ngram_tokens_fn, filter_ngram_tokens_fn, concat_ngram_tokens_fn):
    """create a pipeline to process ngram tokens.

    Args:
        training_model_fn (_type_): a function that takes a list of tokenised texts and returns a model
        get_ngram_tokens_fn (_type_): a function that takes a model and a list of tokenised texts, applies the model to each tokenised text
        filter_ngram_tokens_fn (_type_): a function for filtering only ngram tokens
        concat_ngram_tokens_fn (_type_): a function for concatenating ngram tokens (removing the delimiter)

    Returns:
        _type_: _description_
    """

    filter_ngram_pipeline = compose(filter_ngram_tokens_fn, concat_ngram_tokens_fn)

    def process(input_tuple):
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
