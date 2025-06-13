import requests
import json
import pandas as pd
import re
from bs4 import BeautifulSoup

from typing import Any, Callable, Generic, TypeVar

from utils.monad.extended_pymonad import Left, Right
from .config import topic_base_url, AUTH_TOKEN, TIMEOUT_SECONDS
from .utils import get_random_user_agent

MaybeResponse = TypeVar("Maybe[requests.Response]")
MaybeSoup = TypeVar("Maybe[BeautifulSoup]")

def retrieve_topic(
    topic_id: int | str, auth_token: str = AUTH_TOKEN, agent: str = get_random_user_agent()
) -> MaybeResponse:
    topic_url = topic_base_url.strip("/")  # remove trailing slash
    topic_url = f"{topic_url}/{topic_id}"

    headers = {'ptauthorize': auth_token, 'User-Agent': agent}

    try:
        response = requests.get(topic_url, headers=headers, timeout=TIMEOUT_SECONDS)
    except Exception as e:
        return Left(f"{e.__class__.__name__}: {e}")

    if response.status_code != 200:
        return Left(f"Response code is not 200 (got {response.status_code})")

    return Right(response)


def extract_topic_soup(soup: BeautifulSoup) -> MaybeSoup:
    """Extract topic soup from the topic page"""
    topic_soup = soup.find(attrs={'class': "display-post-wrapper main-post type"})
    if topic_soup is None:
        return Left("Cannot find topic section")
    return Right(topic_soup)


def extract_topic_detail(soup: BeautifulSoup) -> str:
    """Extract HTML string from topic soup"""
    try:
        topic_detail = soup.find(attrs={'class': "display-post-story"}).text
        return Right(topic_detail)
    except Exception as e:
        return Left(f"{e.__class__.__name__}: {e}")
