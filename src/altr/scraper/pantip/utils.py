import requests
import random
from typing import Any, Callable, Generic, TypeVar
from bs4 import BeautifulSoup
import json

from utils.monad.extended_pymonad import Left, Right

from .config import AGENTS

MaybeJSON = TypeVar("Maybe[dict | list[dict]]")
MaybeSoup = TypeVar("Maybe[BeautifulSoup]")


def get_random_user_agent(agents: list[str] = AGENTS) -> str:
    """Get random user agent from config"""
    return random.choice(agents)


def convert_response_to_json(response: requests.Response) -> MaybeJSON:
    """Convert response to json"""
    try:
        return Right(response.json())
    except Exception as e:
        return Left(f"{e.__class__.__name__}: {e}")


def convert_response_content_to_json(response: requests.Response) -> MaybeJSON:
    """Convert response to json (use json.loads(response.content))"""
    try:
        return Right(json.loads(response.content))
    except Exception as e:
        return Left(f"{e.__class__.__name__}: {e}")


def convert_response_to_soup(response: requests.Response) -> MaybeSoup:
    try:
        soup = BeautifulSoup(response.content, 'html.parser')
        return Right(soup)
    except Exception as e:
        return Left(f"{e.__class__.__name__}: {e}")


def extract_json_key(json: dict, key: str) -> MaybeJSON:
    """Extract json key"""
    if key not in json.keys():
        return Left(f"Cannot find key {key} in json")
    return Right(json[key])
