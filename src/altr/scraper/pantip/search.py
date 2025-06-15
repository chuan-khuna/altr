"""
Pantip search scraper module.

This module handles searching for topics on Pantip forums and extracting search results.
"""

import re
import requests
from typing import Optional, List

from altr.monad.extended_pymonad import Left, Right, Either
from .config import SEARCH_API, AUTH_TOKEN, TIMEOUT_SECONDS
from .utils import get_random_user_agent, response_to_json, extract_json_key, MaybeJSON

# Type aliases
MaybeResponse = Either[str, requests.Response]
MaybeInt = Either[str, int]
MaybeStrList = Either[str, List[str]]


def search_topics(
    keyword: str,
    rooms: Optional[List[str]] = None,
    page: int = 1,
    auth_token: str = AUTH_TOKEN,
    user_agent: Optional[str] = None,
    sort_by_time: bool = False,
) -> MaybeResponse:
    """Search for topics on Pantip based on keyword and filters.

    Args:
        keyword: The search term
        rooms: List of room categories to filter by (None for all rooms)
        page: The page number of search results
        auth_token: Authorization token for Pantip API
        user_agent: User agent string to use for the request
                   (will use random one if None)
        sort_by_time: Whether to sort results by time (True) or relevance (False)

    Returns:
        Either[str, requests.Response]: Right containing response on success,
                                       Left containing error message on failure
    """
    if rooms is None:
        rooms = []

    if user_agent is None:
        user_agent = get_random_user_agent()

    headers = {'ptauthorize': auth_token, 'User-Agent': user_agent}
    request_json = {"keyword": keyword, "page": page, 'rooms': rooms, 'timebias': sort_by_time}

    try:
        response = requests.post(SEARCH_API, headers=headers, json=request_json, timeout=TIMEOUT_SECONDS)
    except Exception as e:
        return Left(f"{e.__class__.__name__}: {e}")

    # Check if the response is valid JSON
    maybe_response_json = response_to_json(response)
    if maybe_response_json.is_left():
        return Left(maybe_response_json.error or "Failed to parse response JSON")

    # Check if the server returned an error
    response_json = maybe_response_json.value
    if response_json.get('success') is False:
        return Left(response_json.get('error_message', 'Unknown error'))

    return Right(response)


def count_total_topics(response_data: dict) -> MaybeInt:
    """Count the total number of topics found in search results.

    Args:
        response_data: Response data from Pantip API

    Returns:
        Either[str, int]: Right containing topic count on success,
                         Left containing error message on failure
    """
    if "total" not in response_data:
        return Left("Key 'total' not found in response data")

    # Extract topic count using regex
    total_text = response_data['total']

    # Try pattern for normal results
    re_pattern = r'พบ\s([\d,]+)\sกระทู้'
    result = re.findall(re_pattern, total_text)

    # Try pattern for "more than X" results
    if not result:
        re_pattern_many = r'พบมากกว่า\s([\d,]+)\sกระทู้'
        result = re.findall(re_pattern_many, total_text)

    if not result:
        return Left("Could not extract topic count from response")

    # Convert to integer, removing commas
    try:
        num_topics = int(result[0].replace(",", ""))
        return Right(num_topics)
    except (ValueError, IndexError):
        return Left(f"Failed to convert '{result[0]}' to integer")


def extract_search_results(response_data: dict) -> MaybeJSON:
    """Extract search result data from response.

    Args:
        response_data: Response data from Pantip API

    Returns:
        Either[str, JSON]: Right containing search data on success,
                          Left containing error message on failure
    """
    return extract_json_key(response_data, 'data')


def extract_topic_ids(topics: List[dict]) -> MaybeStrList:
    """Extract the IDs of topics from search results.

    Args:
        topics: List of topic data dictionaries

    Returns:
        Either[str, List[str]]: Right containing list of topic IDs on success,
                               Left containing error message on failure
    """
    if not topics:
        return Right([])  # Empty list is valid

    ids = []
    for topic in topics:
        maybe_id = extract_json_key(topic, 'id')
        if maybe_id.is_right():
            ids.append(maybe_id.value)

    if not ids and topics:
        return Left("Could not extract any IDs from topics")

    return Right(ids)
