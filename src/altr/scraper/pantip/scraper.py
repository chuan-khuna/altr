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
from .utils import response_to_soup, response_to_json
from .comment import fetch_comments, extract_comments, count_comment_pages
from .search import search_topics, extract_search_results, count_total_topics, extract_topic_ids

# Configure logger
logger = logging.getLogger(__name__)

# Type aliases for internal use (not exposed in method signatures)
# These help with casting and type checking
_MaybeComments = Either[str, List[Dict[str, Any]]]
_MaybeSearchResults = Either[str, List[Dict[str, Any]]]


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
            error_msg = f"Failed to fetch topic {topic_id}: {typed_result.monoid[0]}"
            logger.error(error_msg)
            return ''

        logger.debug(f"Successfully fetched topic {topic_id}")
        return typed_result.value

    def get_topic_comments(self, topic_id: Union[str, int], page: int = 1) -> List[Dict[str, Any]]:
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
        result = response.bind(response_to_json).bind(extract_comments)

        # Cast to the correct type for type checking
        typed_result = cast(_MaybeComments, result)

        # Handle the result
        if typed_result.is_left():
            error_msg = f"Failed to fetch comments for topic {topic_id}, page {page}: {typed_result.monoid[0]}"
            logger.error(error_msg)
            return []

        logger.debug(f"Successfully fetched comments for topic {topic_id}, page {page}")
        return typed_result.value

    def get_comment_page_count(self, topic_id: Union[str, int]) -> int:
        """Get the total number of comment pages for a topic.

        Args:
            topic_id: The ID of the topic to get comment page count for

        Returns:
            The number of comment pages, or 0 on failure
        """
        logger.debug(f"Getting comment page count for topic {topic_id}")

        # Fetch the first page of comments to get the total count
        response = fetch_comments(
            topic_id=topic_id, page=1, auth_token=self.auth_token, user_agent=self._random_user_agent()
        )

        # Process the response to get page count
        result = response.bind(response_to_json).bind(count_comment_pages)

        if result.is_left():
            error_msg = f"Failed to get comment page count for topic {topic_id}: {result.monoid[0]}"
            logger.error(error_msg)
            return 0

        logger.debug(f"Topic {topic_id} has {result.value} pages of comments")
        return result.value

    def get_all_topic_comments(self, topic_id: Union[str, int]) -> List[Dict[str, Any]]:
        """Get all comments for a topic across all pages.

        Args:
            topic_id: The ID of the topic to get all comments for

        Returns:
            A list of all comment dictionaries across all pages
        """
        logger.debug(f"Getting all comments for topic {topic_id}")

        # Get the total number of pages
        total_pages = self.get_comment_page_count(topic_id)
        if total_pages == 0:
            logger.error(f"Could not determine comment page count for topic {topic_id}")
            return []

        # Fetch all pages of comments
        all_comments: List[Dict[str, Any]] = []
        for page in range(1, total_pages + 1):
            page_comments = self.get_topic_comments(topic_id, page)
            # page_comments will be empty list on failure, so safe to extend
            all_comments.extend(page_comments)
            if not page_comments:
                logger.warning(f"Failed to fetch comments for page {page}")

        logger.info(f"Retrieved {len(all_comments)} total comments for topic {topic_id}")
        return all_comments

    def search(
        self,
        keyword: str,
        rooms: Optional[List[str]] = None,
        page: int = 1,
        sort_by_time: bool = False,
    ) -> List[Dict[str, Any]]:
        """Search for topics on Pantip based on keyword and filters.

        Args:
            keyword: The search term
            rooms: List of room categories to filter by (None for all rooms)
            page: The page number of search results (defaults to 1)
            sort_by_time: Whether to sort results by time (True) or relevance (False)

        Returns:
            A list of search result dictionaries, or an empty list on failure
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

        # Process the response through the monad chain
        result = response.bind(response_to_json).bind(extract_search_results)

        # Cast to the correct type for type checking
        typed_result = cast(_MaybeSearchResults, result)

        # Handle the result
        if typed_result.is_left():
            error_msg = f"Failed to search for '{keyword}': {typed_result.monoid[0]}"
            logger.error(error_msg)
            return []

        logger.debug(f"Successfully searched for '{keyword}'")
        return typed_result.value

    def get_search_result_count(self, keyword: str, rooms: Optional[List[str]] = None) -> int:
        """Get the total number of search results for a keyword.

        Args:
            keyword: The search term
            rooms: List of room categories to filter by (None for all rooms)

        Returns:
            The number of search results, or 0 on failure
        """
        logger.debug(f"Getting search result count for '{keyword}' in rooms {rooms or 'all'}")

        # Perform the search to get the count
        response = search_topics(
            keyword=keyword, rooms=rooms, auth_token=self.auth_token, user_agent=self._random_user_agent()
        )

        # Process the response to get count
        result = response.bind(response_to_json).bind(count_total_topics)

        if result.is_left():
            error_msg = f"Failed to get search result count for '{keyword}': {result.monoid[0]}"
            logger.error(error_msg)
            return 0

        logger.debug(f"Search for '{keyword}' returned {result.value} results")
        return result.value

    def get_search_result_topic_ids(
        self, keyword: str, rooms: Optional[List[str]] = None, page: int = 1, sort_by_time: bool = False
    ) -> List[str]:
        """Get the topic IDs from search results.

        Args:
            keyword: The search term
            rooms: List of room categories to filter by (None for all rooms)
            page: The page number of search results (defaults to 1)
            sort_by_time: Whether to sort results by time (True) or relevance (False)

        Returns:
            A list of topic IDs from the search results, or empty list on failure
        """
        logger.debug(f"Getting topic IDs for search '{keyword}' in rooms {rooms or 'all'}, page {page}")

        # Get the search results
        search_results = self.search(keyword, rooms, page, sort_by_time)
        # search_results will be an empty list on failure
        if not search_results:
            logger.debug(f"No search results found for '{keyword}'")
            return []

        # Extract topic IDs
        result = extract_topic_ids(search_results)

        if result.is_left():
            error_msg = f"Failed to extract topic IDs from search results: {result.monoid[0]}"
            logger.error(error_msg)
            return []

        logger.debug(f"Found {len(result.value)} topic IDs for search '{keyword}'")
        return result.value
