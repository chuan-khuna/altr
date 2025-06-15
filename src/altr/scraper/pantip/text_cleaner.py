import re
import html
from bs4 import BeautifulSoup

PANTIP_SPOIL_PATTERN = re.compile(r"\[Spoil\] คลิกเพื่อดูข้อความที่ซ่อนไว้")
EDIT_TEXT_PATTERN = re.compile(r"แก้ไขข้อความเมื่อ")
PANTIP_SPACE_PATTERN = [re.compile(r"\{\{eem\}\}"), re.compile(r"\{\{em\}\}")]


def replace_spoil_component(text: str) -> str:
    return PANTIP_SPOIL_PATTERN.sub("", text)


def replace_edit_text(text: str) -> str:
    return EDIT_TEXT_PATTERN.sub("", text)


def replace_pantip_spaces(text: str) -> str:
    for pattern in PANTIP_SPACE_PATTERN:
        text = pattern.sub("", text)
    return text


def remove_leading_trailing_spaces(text: str) -> str:
    return text.strip()


def unescape_html(text: str) -> str:
    return html.unescape(text)


def remove_html_tags(text: str) -> str:
    return BeautifulSoup(text, "html.parser").get_text()


def clean_pantip_text(text: str, remove_punctuations: bool = True, base_clean_func=None) -> str:
    text = replace_spoil_component(text)
    text = replace_edit_text(text)
    text = replace_pantip_spaces(text)
    text = unescape_html(text)
    text = remove_html_tags(text)
    text = remove_leading_trailing_spaces(text)
    if base_clean_func:
        text = base_clean_func(text, remove_punctuations=remove_punctuations)
    return text
