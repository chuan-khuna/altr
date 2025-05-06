from ._types import Token
import gensim
from ._utils import compose

NGRAM_DELIMITER = "<DELIM>"


def prepare_data_for_ngram(
    tokenised_texts: list[list[Token]],
) -> tuple[dict[int, gensim.models.Phrases | None], dict[int, list[list[Token]]], dict[int, list[list[Token]]]]:
    """prepare a list of tokenised texts for ngram model

    Args:
        tokenised_texts (list[list[Token]]): _description_

    Returns:
        tuple[dict[int, gensim.models.Phrases | None], dict[int, list[list[Token]]], dict[int, list[list[Token]]]]:

        tuple of dictionaries
        - the first dictionary contains the ngram models
        - the second dictionary contains the tokenised texts (for training ngram models)
        - the third dictionary contains the n-gram tokens
    """
    return ({1: None}, {1: tokenised_texts}, {1: tokenised_texts})


def _train_ngram_model(model_kwargs: dict, tokenised_texts: list[Text]) -> gensim.models.Phrases:
    model = gensim.models.Phrases(tokenised_texts, delimiter=NGRAM_DELIMITER, **model_kwargs)
    return model


def _get_ngram_tokens(model: gensim.models.Phrases, tokenised_texts: list[list[Token]]) -> list[list[Token]]:
    return [model[tokens] for tokens in tokenised_texts]


def _fit_transform_ngram_models(
    model_kwargs,
    tokenised_texts: list[list[Token]],
):
    model = _train_ngram_model(model_kwargs, tokenised_texts)
    result = _get_ngram_tokens(model, tokenised_texts)
    return model, result


def _filter_only_ngram_tokens(tokenised_texts: list[list[Token]]) -> list[list[Token]]:
    return [[token for token in tokens if NGRAM_DELIMITER in token] for tokens in tokenised_texts]


def _concat_ngram_tokens(tokenised_texts: list[list[Token]]) -> list[list[Token]]:
    return [[token.replace(NGRAM_DELIMITER, "") for token in tokens] for tokens in tokenised_texts]


def process_ngram(model_kwargs):
    filter_ngram_pipeline = compose(_filter_only_ngram_tokens, _concat_ngram_tokens)

    def process(input_tuple):
        # extract data from input tuple
        models = input_tuple[0]
        ngram_tokens = input_tuple[1]
        ngram_tokens_filtered = input_tuple[2]

        # find the previous number of ngram
        max_available_ngram = max(models.keys())
        next_ngram = max_available_ngram + 1

        # get previous ngram tokens
        # and use them for training the ngram model
        model_input = ngram_tokens[max_available_ngram]

        model, ngram_result = _fit_transform_ngram_models(model_kwargs, model_input)
        # filter only ngram tokens
        ngram_result_filtered = filter_ngram_pipeline(ngram_result)
        ngram_result = _concat_ngram_tokens(ngram_result)

        # assign data to the memory
        models[next_ngram] = model
        ngram_tokens[next_ngram] = ngram_result
        ngram_tokens_filtered[next_ngram] = ngram_result_filtered

        return models, ngram_tokens, ngram_tokens_filtered

    return process
