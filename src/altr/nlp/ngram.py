from ._types import Token, NgramInfo, NgramContext
from ._utils import compose

from copy import deepcopy
from typing import Callable


def prepare_data_for_ngram(
    tokenised_texts: list[list[Token]],
) -> NgramContext:
    """Initialise ngram processing structures.

    Returns:
        NgramContext with n=1 (unigram) initialized with the tokenised texts.
    """
    ngram_info = NgramInfo(
        n=1, tokenised_texts=tokenised_texts, filtered_ngram_tokenised_texts=tokenised_texts, model=None
    )
    return NgramContext(ns={1: ngram_info})


def process_ngram(
    training_model_fn: Callable[[list[list[Token]]], object],
    get_ngram_tokens_fn: Callable[[object, list[list[Token]]], list[list[Token]]],
    filter_ngram_tokens_fn: Callable[[list[list[Token]]], list[list[Token]]],
    concat_ngram_tokens_fn: Callable[[list[list[Token]]], list[list[Token]]],
) -> Callable[[NgramContext], NgramContext]:
    """
    Creates a pipeline to process n-gram tokens.

    This function generates a callable pipeline that processes n-gram tokens
    by training a model, generating n-gram tokens, filtering them, and
    concatenating the results. It updates the input data structures with
    the processed n-gram tokens.

    Args:
        training_model_fn (Callable): A function that trains a model using
            a list of tokenized texts.
            Signature: `list[list[Token]] -> object`.

        get_ngram_tokens_fn (Callable): A function that generates n-gram tokens (ie, tokenised_texts but n-gram tokens included)
            using a trained model and tokenized texts.
            Signature: `(object, list[list[Token]]) -> list[list[Token]]`.

        filter_ngram_tokens_fn (Callable): A function that filters n-gram tokens
            from the input tokenized texts.
            Signature: `list[list[Token]] -> list[list[Token]]`.

        concat_ngram_tokens_fn (Callable): A function that concatenates n-gram
            tokens by removing delimiters.
            Signature: `list[list[Token]] -> list[list[Token]]`.

    Returns:
        Callable: A function that takes an NgramContext and returns an updated
            NgramContext with the next n-gram level processed and added.
    """

    filter_ngram_pipeline = compose(filter_ngram_tokens_fn, concat_ngram_tokens_fn)

    def process(context: NgramContext) -> NgramContext:
        # find the previous number of ngram
        max_ngram = max(context.ns.keys())
        next_ngram = max_ngram + 1

        # get the previous ngram info
        prev_ngram_info = context.ns[max_ngram]
        model_input = prev_ngram_info.tokenised_texts

        # train model and generate ngram tokens
        model = training_model_fn(model_input)
        ngram_result = get_ngram_tokens_fn(model, model_input)

        # filter only ngram tokens
        ngram_result_filtered = filter_ngram_pipeline(ngram_result)
        ngram_result = concat_ngram_tokens_fn(ngram_result)

        # create new NgramInfo for next level
        new_ngram_info = NgramInfo(
            n=next_ngram,
            tokenised_texts=ngram_result,
            filtered_ngram_tokenised_texts=ngram_result_filtered,
            model=model,
        )

        # return new context, avoid mutation
        new_ns = deepcopy(context.ns)
        new_ns[next_ngram] = new_ngram_info

        return NgramContext(ns=new_ns)

    return process
