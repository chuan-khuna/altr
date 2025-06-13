import requests
import json
import pandas as pd
import numpy as np
import re
from bs4 import BeautifulSoup


from typing import Any, Callable, Generic, TypeVar

from utils.monad.extended_pymonad import Left, Right
from .config import comment_api, AUTH_TOKEN, TIMEOUT_SECONDS
from .utils import get_random_user_agent, extract_json_key

MaybeResponse = TypeVar("Maybe[requests.Response]")
MaybeInt = TypeVar("Maybe[int]")
MaybeJSON = TypeVar("Maybe[dict | list[dict]]")

def retrieve_comments_list(
    topic_id: int | str,
    page: int,
    auth_token: str = AUTH_TOKEN,
    agent: str = get_random_user_agent(),
) -> MaybeResponse:
    params = {'tid': str(topic_id), 'param': f'page{page}'}
    headers = {'x-requested-with': 'XMLHttpRequest', 'ptauthorize': auth_token, 'User-Agent': agent}

    try:
        response = requests.get(
            comment_api, params=params, headers=headers, timeout=TIMEOUT_SECONDS
        )
    except Exception as e:
        return Left(f"{e.__class__.__name__}: {e}")

    if response.status_code != 200:
        return Left(f"Response code is not 200 (got {response.status_code})")

    return Right(response)


def extract_number_of_comments(response: dict) -> MaybeInt:
    extract_page = lambda json_dict: extract_json_key(json_dict, 'paging')
    extract_max_comments = lambda json_dict: extract_json_key(json_dict, 'max_comments')

    maybe_max_comments = extract_page(response) >> extract_max_comments
    if maybe_max_comments.is_left():
        return maybe_max_comments

    num_page = int(np.ceil(maybe_max_comments.value / 100))
    return Right(num_page)


def extract_comment_data(response: dict) -> MaybeJSON:
    return extract_json_key(response, 'comments')
