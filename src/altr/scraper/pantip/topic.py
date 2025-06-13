"""
Pantip topic scraper module.

This module handles fetching and processing topic content from Pantip forums.
"""

import requests
from typing import Union, Optional
from bs4 import BeautifulSoup, Tag

from altr.monad.extended_pymonad import Left, Right, Either
from .config import TOPIC_BASE_URL, AUTH_TOKEN, TIMEOUT_SECONDS
from .utils import get_random_user_agent

# Type aliases
MaybeResponse = Either[str, requests.Response]
MaybeTag = Either[str, Tag]
MaybeStr = Either[str, str]


def fetch_topic(
    topic_id: Union[int, str], auth_token: str = AUTH_TOKEN, user_agent: Optional[str] = None
) -> MaybeResponse:
    """Fetch a topic page from Pantip.

    Args:
        topic_id: The ID of the topic to fetch
        auth_token: Authorization token for Pantip API
        user_agent: User agent string to use for the request
                   (will use random one if None)

    Returns:
        Either[str, requests.Response]: Right containing response on success,
                                       Left containing error message on failure
    """
    if user_agent is None:
        user_agent = get_random_user_agent()

    # Normalize URL to ensure proper format
    topic_url = f"{TOPIC_BASE_URL.rstrip('/')}/{topic_id}"
    headers = {'ptauthorize': auth_token, 'User-Agent': user_agent}

    try:
        response = requests.get(topic_url, headers=headers, timeout=TIMEOUT_SECONDS)
    except Exception as e:
        return Left(f"{e.__class__.__name__}: {e}")

    if response.status_code != 200:
        return Left(f"Response code is not 200 (got {response.status_code})")

    return Right(response)


def extract_topic_content(soup: BeautifulSoup) -> MaybeTag:
    """Extract the main content section from a topic page.

    Args:
        soup: BeautifulSoup object of the topic page

    Returns:
        Either[str, Tag]: Right containing content section on success,
                         Left containing error message on failure
    """
    # topic content is the detail section of the topic
    # the first main post written by the topic creator
    topic_content = soup.find(attrs={'class': "display-post-wrapper main-post type"})
    if topic_content is None:
        return Left("Cannot find topic content section")
    if not isinstance(topic_content, Tag):
        return Left("Found content is not a Tag element")
    return Right(topic_content)


def extract_topic_text(soup: BeautifulSoup) -> MaybeStr:
    """Extract the text content from a topic.

    Args:
        soup: BeautifulSoup object of the topic content section

    Returns:
        Either[str, str]: Right containing text content on success,
                         Left containing error message on failure
    """
    try:
        content_section = soup.find(attrs={'class': "display-post-story"})
        if content_section is None:
            return Left("Cannot find content section in topic")
        return Right(content_section.text)
    except Exception as e:
        return Left(f"{e.__class__.__name__}: {e}")
