"""
Pantip Scraper module.

This module provides a high-level OOP interface for scraping data from Pantip forums.
It handles authentication, request management, and data extraction with proper error handling.
"""

import random
import logging
from typing import Union, List, Dict, Any, cast, Optional

from altr.monad.extended_pymonad import Either
from .config import USER_AGENTS, TIMEOUT_SECONDS, AUTH_TOKEN
from .topic import fetch_topic, extract_topic_content, extract_topic_text, MaybeStr
from .utils import response_to_soup, response_to_json, response_content_to_json
from .comment import fetch_comments, extract_comments, count_comment_pages
from .search import search_topics, extract_search_results, count_total_topics, extract_topic_ids

# Configure logger
logger = logging.getLogger(__name__)

# Type aliases for internal use (not exposed in method signatures)
# These help with casting and type checking
_MaybeComments = Either[str, List[Dict[str, Any]]]


class PantipScraper:
    """A high-level interface for scraping Pantip data.

    This class provides methods to retrieve topic content, comments, and perform searches
    with proper error handling and logging.

    All methods return unwrapped values (not monads) for a simpler API:
    - Successful calls return the actual data (string, list, etc.)
    - Failed calls return appropriate identity values (empty string, empty list, etc.)
    - Error details are logged but not exposed in return values

    Attributes:
        auth_token (str): Authentication token for Pantip API
        user_agents (List[str]): List of user agent strings to rotate through
        timeout (int): Timeout in seconds for HTTP requests
    """

    def __init__(
        self,
        auth_token: str = AUTH_TOKEN,
        user_agents: Optional[List[str]] = None,
        timeout: int = TIMEOUT_SECONDS,
        log_level: int = logging.INFO,
    ):
        """Initialize the PantipScraper.

        Args:
            auth_token: Authentication token for Pantip API
            user_agents: List of user agent strings to rotate through (uses defaults if None)
            timeout: Timeout in seconds for HTTP requests
            log_level: Logging level to use
        """
        self.auth_token = auth_token
        self.user_agents = user_agents if user_agents is not None else USER_AGENTS
        self.timeout = timeout

        # Configure logger
        self._setup_logger(log_level)

    def _setup_logger(self, log_level: int) -> None:
        """Set up the logger for this instance.

        Args:
            log_level: Logging level to use
        """
        logger.setLevel(log_level)
        # Only add handler if none exists to prevent duplicate log messages
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '[%(levelname)s] %(asctime)s.%(msecs)03d - %(name)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)

    def _random_user_agent(self) -> str:
        """Get a random user agent from the configured list.

        Returns:
            A randomly selected user agent string
        """
        return random.choice(self.user_agents)

    def get_topic_detail(self, topic_id: Union[str, int]) -> str:
        """Fetch and extract the main content of a Pantip topic.

        Args:
            topic_id: The ID of the topic to fetch

        Returns:
            The topic content as a string, or an empty string on failure
        """
        logger.debug(f"Fetching topic {topic_id}")

        # Get the topic content
        response = fetch_topic(topic_id=topic_id, auth_token=self.auth_token, user_agent=self._random_user_agent())

        # Process the response through the monad chain
        # We need to use .bind() instead of >> operator to help type checker
        result = response.bind(response_to_soup).bind(extract_topic_content).bind(extract_topic_text)

        # Cast the result to the proper type for type checking
        typed_result = cast(MaybeStr, result)

        # Handle the result based on the MaybeStr type
        if typed_result.is_left():
            error_msg = f"Failed to fetch topic {topic_id}: {typed_result.error}"
            logger.error(error_msg)
            return ''

        logger.debug(f"Successfully fetched topic {topic_id}")
        return typed_result.value

    def get_topic_comments(self, topic_id: Union[str, int], page: int = 1) -> Dict[str, Any]:
        """Fetch comments for a Pantip topic.

        Args:
            topic_id: The ID of the topic to fetch comments for
            page: The page number of comments to fetch (defaults to 1)

        Returns:
            A list of comment dictionaries, or an empty list on failure
        """
        logger.debug(f"Fetching comments for topic {topic_id}, page {page}")

        # Get the comments
        response = fetch_comments(
            topic_id=topic_id, page=page, auth_token=self.auth_token, user_agent=self._random_user_agent()
        )

        # Process the response through the monad chain
        response_json = response.bind(response_content_to_json)
        result = response_json.bind(extract_comments)
        page_count = response_json.bind(count_comment_pages)

        if result.is_left():
            error_msg = f"Failed to fetch comments for topic {topic_id}, page {page}: {result.error}"
            logger.error(error_msg)
            return {
                "data": [],
                "page_count": 0,
                "error": error_msg,
            }

        logger.debug(f"Successfully fetched comments for topic {topic_id}, page {page}")
        return {
            "data": result.value,
            "page_count": page_count.value,
            "error": None,  # No error
        }

    def search(
        self,
        keyword: str,
        rooms: Optional[List[str]] = None,
        page: int = 1,
        sort_by_time: bool = False,
    ) -> Dict[str, Any]:
        """_summary_

        Args:
            keyword (str): _description_
            rooms (Optional[List[str]], optional): _description_. Defaults to None.
            page (int, optional): _description_. Defaults to 1.
            sort_by_time (bool, optional): _description_. Defaults to False.

        Returns:
            Dict[str, Any]: _description_
        """
        logger.debug(f"Searching for '{keyword}' in rooms {rooms or 'all'}, page {page}")

        # Perform the search
        response = search_topics(
            keyword=keyword,
            rooms=rooms,
            page=page,
            auth_token=self.auth_token,
            user_agent=self._random_user_agent(),
            sort_by_time=sort_by_time,
        )

        # Convert response to JSON
        response_json = response.bind(response_to_json)
        topic_data = response_json.bind(extract_search_results)
        topic_ids = topic_data.bind(extract_topic_ids)
        num_topics = response_json.bind(count_total_topics)

        # Handle errors in the response
        if response_json.is_left():
            error_msg = f"Search failed: {response_json.error}"
            logger.error(error_msg)
            return {"data": None, "topic_ids": None, "total_topics": None} | {"error": error_msg}

        return {
            "data": topic_data.value,
            "topic_ids": topic_ids.value,
            "total_topics": num_topics.value,
            "error": None,
        }
