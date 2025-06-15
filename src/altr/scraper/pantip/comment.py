"""
Pantip comment scraper module.

This module handles fetching and processing comments from Pantip forum topics.
"""
import math
import requests
from typing import Union, Optional

from altr.monad.extended_pymonad import Left, Right, Either
from .config import COMMENT_API, AUTH_TOKEN, TIMEOUT_SECONDS
from .utils import get_random_user_agent, extract_json_key, MaybeJSON

# Type aliases
MaybeResponse = Either[str, requests.Response]
MaybeInt = Either[str, int]


def fetch_comments(
    topic_id: Union[int, str],
    page: int,
    auth_token: str = AUTH_TOKEN,
    user_agent: Optional[str] = None,
) -> MaybeResponse:
    """Fetch comments for a specific topic and page.
    
    Args:
        topic_id: The ID of the topic to fetch comments for
        page: The page number of comments to fetch
        auth_token: Authorization token for Pantip API
        user_agent: User agent string to use for the request
                   (will use random one if None)
    
    Returns:
        Either[str, requests.Response]: Right containing response on success,
                                       Left containing error message on failure
    """
    if user_agent is None:
        user_agent = get_random_user_agent()
        
    params = {'tid': str(topic_id), 'param': f'page{page}'}
    headers = {
        'x-requested-with': 'XMLHttpRequest', 
        'ptauthorize': auth_token, 
        'User-Agent': user_agent
    }

    try:
        response = requests.get(
            COMMENT_API, params=params, headers=headers, timeout=TIMEOUT_SECONDS
        )
    except Exception as e:
        return Left(f"{e.__class__.__name__}: {e}")

    if response.status_code != 200:
        return Left(f"Response code is not 200 (got {response.status_code})")

    return Right(response)


def count_comment_pages(response_data: dict) -> MaybeInt:
    """Calculate the number of pages of comments based on response data.
    
    Args:
        response_data: Response data from Pantip API
        
    Returns:
        Either[str, int]: Right containing number of pages on success,
                         Left containing error message on failure
    """
    # Extract max comments from paging information
    maybe_paging = extract_json_key(response_data, 'paging')
    if maybe_paging.is_left():
        return Left(maybe_paging.error or "Failed to extract paging")
        
    maybe_max_comments = extract_json_key(maybe_paging.value, 'max_comments')
    if maybe_max_comments.is_left():
        return Left(maybe_max_comments.error or "Failed to extract max_comments")

    # Calculate number of pages (100 comments per page)
    num_pages = math.ceil(maybe_max_comments.value / 100)
    return Right(num_pages)


def extract_comments(response_data: dict) -> MaybeJSON:
    """Extract comments data from response.
    
    Args:
        response_data: Response data from Pantip API
        
    Returns:
        Either[str, JSON]: Right containing comments data on success,
                          Left containing error message on failure
    """
    return extract_json_key(response_data, 'comments')
