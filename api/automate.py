import json
import time

import requests

from api.article import html_format_data, add_article, get_last_kw
from api.extract import extract_youtube

from typing import Generator
from config import CATEGORY_ID
sess = requests.Session()

def process(client, keyword):
    links = extract_youtube(keyword)
    if links:
        html = html_format_data(links, keyword)

        if add_article(keyword, html, client):
            return True
        else:
            return False
    else:
        return False


def process_keywords(DB_NAME):
    with open(DB_NAME, 'r', encoding='utf-8') as f:
        kws = json.load(f)
    last_keyword = get_last_kw(sess)
    print(last_keyword)
    completed: list = kws.get("COMPLETED")
    uncompleted: list = kws.get("UNCOMPLETED")
    try:
        last_keyword_index = uncompleted.index(last_keyword)
    except ValueError:
        last_keyword_index = 0

    if last_keyword_index > 0:
        completed.extend(uncompleted[:last_keyword_index + 1])
        for i in reversed(range(0, last_keyword_index + 1)):
            uncompleted.pop(i)

        update_keywords(DB_NAME, completed, uncompleted)

    item_len = len(uncompleted)
    i = 0
    while i <= item_len:
        keyword = uncompleted[i]
        display_status(keyword, i, item_len - i)
        status = process(sess, keyword)
        if not status:
            uncompleted.append(keyword)
            time.sleep(0.5)
        i += 1


def update_keywords(DB_NAME, completed_words, uncompleted_words):
    with open(DB_NAME, 'w', encoding='utf-8') as f:
        kws = {"COMPLETED": completed_words, "UNCOMPLETED": uncompleted_words}
        json.dump(kws, f)

def save_keywords(db_name: str, keywords: Generator):
    dct = {"UNCOMPLETED": [], "COMPLETED": []}
    for kw in keywords:
        dct.get("UNCOMPLETED").append(kw)
    with open(db_name, 'w', encoding='utf-8') as f:
        json.dump(dct, f)


def display_status(keyword, current_completed_count, uncompleted_count):
    print(f"""
    |===============================================|
    |   Keyword Left:  {uncompleted_count}
    |   Current Status: {current_completed_count + 1} Completed!
    |   Current keyword: {keyword}                  
    |===============================================|
    """)


