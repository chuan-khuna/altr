# this file focusing on pantip seach page
# the function to list all topics for a keyword

import requests
import json
import pandas as pd
import re

from typing import Any, Callable, Generic, TypeVar

from utils.monad.extended_pymonad import Left, Right
from .config import search_api, AUTH_TOKEN, TIMEOUT_SECONDS
from .utils import get_random_user_agent, convert_response_to_json, extract_json_key

MaybeResponse = TypeVar("Maybe[requests.Response]")
MaybeInt = TypeVar("Maybe[int]")
MaybeJSON = TypeVar("Maybe[dict | list[dict]]")
MaybeListIds = TypeVar("Maybe[list[str]]")


def retrieve_topics_list(
    keyword: str,
    rooms: list[str] = [],
    page: int = 1,
    auth_token: str = AUTH_TOKEN,
    agent: str = get_random_user_agent(),
    sort_by_time: bool = False,
) -> MaybeResponse:
    """_summary_

    Args:
        keyword (str): _description_
        rooms (list[str], optional): _description_. Defaults to [].
        page (int, optional): pagination of the API (defualt to 10 topics per page). Defaults to 1.
        auth_token (str, optional): _description_. Defaults to AUTH_TOKEN.
        agent (str, optional): string or a function that returns string to randomly pick the agent. Defaults to get_random_user_agent().
        sort_by_time (bool, optional): whether to sort the result by time or not. Defaults to False.

    Returns:
        MaybeResponse
    """

    headers = {'ptauthorize': auth_token, 'User-Agent': agent}
    request_json = {"keyword": keyword, "page": page, 'rooms': rooms, 'timebias': sort_by_time}

    try:
        response = requests.post(
            search_api, headers=headers, json=request_json, timeout=TIMEOUT_SECONDS
        )
    except Exception as e:
        return Left(f"{e.__class__.__name__}: {e}")

    # extract json from response
    # for checking if the response is success or not
    maybe_response_json = convert_response_to_json(response)
    if maybe_response_json.is_left():
        return maybe_response_json

    response_json = maybe_response_json.value

    if response.status_code != 200:
        return Left(f"Response code is not 200 (got {response.status_code})")

    # check if the server response is success or not
    if response_json['success'] == False:
        return Left(response_json['error_message'])

    return Right(response)


def extract_number_of_topics(response: dict) -> MaybeInt:
    if "total" not in response.keys():
        return Left("key `total` not in response")

    re_pattern = r'พบ\s([\d,]+)\sกระทู้'
    result = re.findall(re_pattern, response['total'])

    re_pattern_many = r'พบมากกว่า\s([\d,]+)\sกระทู้'
    result_many = re.findall(re_pattern_many, response['total'])

    result = result + result_many

    if len(result) == 0:
        return Left("Regex pattern cannot find number of topics")

    num_topic = int(re.sub(",", "", result[0]))
    return Right(num_topic)


def extract_search_data(response: dict) -> MaybeJSON:
    return extract_json_key(response, 'data')


def extract_topic_ids(topics: list[dict]) -> MaybeListIds:
    """return list of topic ids from list of topics"""
    ids = []
    for topic in topics:
        id = extract_json_key(topic, 'id')
        if id.is_right():
            ids.append(id.value)
    return Right(ids)
