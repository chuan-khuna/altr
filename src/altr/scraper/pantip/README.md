# Pantip Scraper

A functional programming approach to scraping Pantip forums.

## Overview

This module provides utilities for scraping content from [Pantip](https://pantip.com/), a popular Thai discussion forum platform. It uses a functional programming style with monads for error handling.

## Modules

- `config.py`: Configuration settings for the scraper
- `utils.py`: Utility functions for requests and data processing
- `search.py`: Functions for searching topics
- `topic.py`: Functions for fetching and parsing topic pages
- `comment.py`: Functions for fetching and parsing comments

## Usage Examples

### Searching for Topics

```python
from altr.scraper.pantip import search_topics, extract_search_results

# Search for topics about "Python programming"
result = search_topics("Python programming")
if result.is_right():
    response = result.value
    # Convert response to JSON
    from altr.scraper.pantip.utils import response_to_json
    json_result = response_to_json(response)
    if json_result.is_right():
        # Extract search results
        search_data = extract_search_results(json_result.value)
        if search_data.is_right():
            topics = search_data.value
            # Process topics...
```

### Fetching a Topic

```python
from altr.scraper.pantip import fetch_topic, extract_topic_text
from altr.scraper.pantip.utils import response_to_soup

# Fetch a topic by ID
topic_id = "12345678"
result = fetch_topic(topic_id)
if result.is_right():
    response = result.value
    # Convert response to BeautifulSoup
    soup_result = response_to_soup(response)
    if soup_result.is_right():
        # Extract topic text
        text_result = extract_topic_text(soup_result.value)
        if text_result.is_right():
            topic_text = text_result.value
            # Process topic text...
```

### Fetching Comments

```python
from altr.scraper.pantip import fetch_comments, extract_comments
from altr.scraper.pantip.utils import response_to_json

# Fetch comments for a topic
topic_id = "12345678"
page = 1
result = fetch_comments(topic_id, page)
if result.is_right():
    response = result.value
    # Convert response to JSON
    json_result = response_to_json(response)
    if json_result.is_right():
        # Extract comments
        comments_result = extract_comments(json_result.value)
        if comments_result.is_right():
            comments = comments_result.value
            # Process comments...
```

## Error Handling

All functions return a monad (`Either[str, T]`) which can be either:

- `Left(error_message)` if an error occurred
- `Right(result)` if the operation was successful

This allows for clean error handling and function composition.
