"""
Utility functions for Pantip scraper.

This module contains helper functions for the Pantip scraper,
including response parsing, error handling, and data extraction.
"""

import json
import random
import requests
from typing import Any
from bs4 import BeautifulSoup

from altr.monad.extended_pymonad import Left, Right, Either

from .config import USER_AGENTS

# Type aliases for better readability
JSON = dict[str, Any] | list[dict[str, Any]]
MaybeJSON = Either[str, JSON]
MaybeSoup = Either[str, BeautifulSoup]
MaybeResponse = Either[str, requests.Response]


def get_random_user_agent() -> str:
    """Get a random user agent from the configured list.

    Returns:
        str: A randomly selected user agent string
    """
    return random.choice(USER_AGENTS)


def response_to_json(response: requests.Response) -> MaybeJSON:
    """Convert response to JSON using response.json().

    Args:
        response: HTTP response object

    Returns:
        Either[str, JSON]: Right containing parsed JSON on success,
                           Left containing error message on failure
    """
    try:
        return Right(response.json())
    except Exception as e:
        return Left(f"{e.__class__.__name__}: {e}")


def response_content_to_json(response: requests.Response) -> MaybeJSON:
    """Convert response content to JSON using json.loads.

    Args:
        response: HTTP response object

    Returns:
        Either[str, JSON]: Right containing parsed JSON on success,
                           Left containing error message on failure
    """
    try:
        return Right(json.loads(response.content))
    except Exception as e:
        return Left(f"{e.__class__.__name__}: {e}")


def response_to_soup(response: requests.Response) -> MaybeSoup:
    """Convert response content to BeautifulSoup object.

    Args:
        response: HTTP response object

    Returns:
        Either[str, BeautifulSoup]: Right containing BeautifulSoup on success,
                                    Left containing error message on failure
    """
    try:
        soup = BeautifulSoup(response.content, 'html.parser')
        return Right(soup)
    except Exception as e:
        return Left(f"{e.__class__.__name__}: {e}")


def extract_json_key(data: dict, key: str) -> MaybeJSON:
    """Extract a value from a JSON dictionary by key.

    Args:
        data: Dictionary to extract from
        key: Key to extract

    Returns:
        Either[str, Any]: Right containing the value if key exists,
                          Left containing error message if not
    """
    if key not in data:
        return Left(f"Cannot find key '{key}' in data")
    return Right(data[key])
