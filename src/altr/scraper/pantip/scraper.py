"""
Pantip Scraper module.

This module provides a high-level OOP interface for scraping data from Pantip forums.
It handles authentication, request management, and data extraction with proper error handling.
"""

import random
import logging
from typing import Union, List, Dict, Any, cast, Optional

from .config import USER_AGENTS, TIMEOUT_SECONDS, AUTH_TOKEN
from .topic import fetch_topic, extract_topic_content, extract_topic_text, MaybeStr
from .utils import response_to_soup, response_to_json, response_content_to_json
from .comment import fetch_comments, extract_comments, count_comment_pages
from .search import search_topics, extract_search_results, count_total_topics, extract_topic_ids

# Configure logger
logger = logging.getLogger(__name__)

# Type aliases for better readability
TopicID = Union[str, int]
SearchResult = Dict[str, Any]
CommentResult = Dict[str, Any]


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

    def _format_error(self, operation: str, entity_id: Any, error: Any) -> str:
        """Format and log an error message for an operation.

        Args:
            operation: Description of the operation that failed
            entity_id: ID or identifier for the entity being processed
            error: The error message or object

        Returns:
            Formatted error message
        """
        error_msg = f"Failed to {operation} {entity_id}: {error}"
        logger.error(error_msg)
        return error_msg

    def get_topic_detail(self, topic_id: TopicID) -> str:
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
        result = response.bind(response_to_soup).bind(extract_topic_content).bind(extract_topic_text)

        # Cast the result to the proper type for type checking
        typed_result = cast(MaybeStr, result)

        # Handle the result based on the Either monad
        if typed_result.is_left():
            self._format_error("fetch topic", topic_id, typed_result.error)
            return ''

        logger.debug(f"Successfully fetched topic {topic_id}")
        return typed_result.value

    def get_topic_comments(self, topic_id: TopicID, page: int = 1) -> CommentResult:
        """Fetch comments for a Pantip topic.

        Args:
            topic_id: The ID of the topic to fetch comments for
            page: The page number of comments to fetch (defaults to 1)

        Returns:
            A dictionary containing:
                - data: List of comment dictionaries
                - page_count: Total number of comment pages
                - error: Error message if any, None otherwise
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
            error_msg = self._format_error("fetch comments for topic", f"{topic_id}, page {page}", result.error)
            return {
                "data": [],
                "page_count": 0,
                "error": error_msg,
            }

        logger.debug(f"Successfully fetched comments for topic {topic_id}, page {page}")
        return {
            "data": result.value,
            "page_count": page_count.value if not page_count.is_left() else 0,
            "error": None,
        }

    def search(
        self,
        keyword: str,
        rooms: Optional[List[str]] = None,
        page: int = 1,
        sort_by_time: bool = False,
    ) -> SearchResult:
        """Search for topics on Pantip based on keywords and filters.

        Args:
            keyword: The search keyword/phrase
            rooms: List of room IDs to search within (None searches all rooms)
            page: The search results page number to fetch
            sort_by_time: If True, sort results by time; otherwise by relevance

        Returns:
            A dictionary containing:
                - data: List of topic dictionaries with search results
                - topic_ids: List of topic IDs from search results
                - total_topics: Total number of topics matching the search
                - error: Error message if any, None otherwise
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

        # Convert response to JSON and extract data
        response_json = response.bind(response_to_json)

        # If JSON conversion failed, return error
        if response_json.is_left():
            error_msg = self._format_error("search for", f"'{keyword}'", response_json.error)
            return {
                "data": [],
                "topic_ids": [],
                "total_topics": 0,
                "error": error_msg,
            }

        # Extract data from the JSON response
        topic_data = response_json.bind(extract_search_results)
        topic_ids = response_json.bind(extract_search_results).bind(extract_topic_ids)
        num_topics = response_json.bind(count_total_topics)

        # Build the result dictionary with proper error handling
        return {
            "data": topic_data.value if not topic_data.is_left() else [],
            "topic_ids": topic_ids.value if not topic_ids.is_left() else [],
            "total_topics": num_topics.value if not num_topics.is_left() else 0,
            "error": None,
        }
