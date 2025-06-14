import random

from .config import USER_AGENTS
from .topic import fetch_topic, extract_topic_content, extract_topic_text
from .utils import response_to_soup

import logging


class TopicClient:
    def __init__(self, auth_token: str, user_agents: list[str] = None):
        self.auth_token = auth_token
        self.user_agents = user_agents if user_agents is not None else USER_AGENTS

    def _random_user_agent(self):
        return random.choice(self.user_agents)

    def get_topic_detail(self, topic_id: str):
        response = fetch_topic(topic_id=topic_id, auth_token=self.auth_token, user_agent=self._random_user_agent())

        result = response >> response_to_soup >> extract_topic_content >> extract_topic_text

        if result.is_left():
            logging.info(f"Failed to fetch topic {topic_id}: {result.left()}")
            return ''

        return result.value
