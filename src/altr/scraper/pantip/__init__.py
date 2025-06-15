"""
Pantip Scraper Package

This package provides utilities for scraping content from Pantip forums,
a popular Thai discussion forum platform.

Modules:
    config: Configuration settings for the scraper
    utils: Utility functions for requests and data processing
    search: Functions for searching topics
    topic: Functions for fetching and parsing topic pages
    comment: Functions for fetching and parsing comments
"""

from .config import AUTH_TOKEN, USER_AGENTS, TIMEOUT_SECONDS, ROOMS
from .search import search_topics, count_total_topics, extract_search_results, extract_topic_ids
from .topic import fetch_topic, extract_topic_content, extract_topic_text
from .comment import fetch_comments, count_comment_pages, extract_comments
from .text_cleaner import clean_pantip_text

__all__ = [
    # Config exports
    'AUTH_TOKEN',
    'USER_AGENTS',
    'TIMEOUT_SECONDS',
    'ROOMS',
    # Search functions
    'search_topics',
    'count_total_topics',
    'extract_search_results',
    'extract_topic_ids',
    # Topic functions
    'fetch_topic',
    'extract_topic_content',
    'extract_topic_text',
    # Comment functions
    'fetch_comments',
    'count_comment_pages',
    'extract_comments',
    # Text cleaning functions
    'clean_pantip_text',
]
