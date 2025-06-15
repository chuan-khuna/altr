"""
Configuration for Pantip scraper.

This module contains all configuration variables used by the Pantip scraper,
including API endpoints, request parameters, and default values.
"""
from typing import Final

# Authorization token for Pantip API
# In production, this should be loaded from environment variables
AUTH_TOKEN: Final[str] = 'Basic dGVzdGVyOnRlc3Rlcg=='

# List of user agents to rotate for requests to avoid detection
USER_AGENTS: Final[list[str]] = [
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_5) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.1.1 Safari/605.1.15',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:77.0) Gecko/20100101 Firefox/77.0',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.97 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:77.0) Gecko/20100101 Firefox/77.0',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.97 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36',
]

# Request parameters
TOPICS_PER_PAGE: Final[int] = 10  # Number of topics per page in search results
TIMEOUT_SECONDS: Final[int] = 4   # Request timeout in seconds

# API Endpoints
SEARCH_API: Final[str] = "https://pantip.com/api/search-service/search/getresult"
TOPIC_BASE_URL: Final[str] = "https://pantip.com/topic/"
COMMENT_API: Final[str] = "https://pantip.com/forum/topic/render_comments"
