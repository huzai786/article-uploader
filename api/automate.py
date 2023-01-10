import requests

from api.article import html_format_data, add_article
from api.extract import extract_youtube

sess = requests.Session()

def process(client, keyword, record):
    links = extract_youtube(keyword)
    if links:
        html = html_format_data(links, keyword)

        if add_article(keyword, html, client):
            record['completed'].append(keyword)
        else:
            record['uncompleted'].append(keyword)
    else:
        record['uncompleted'].append(keyword)


def process_keywords(keywords: list):
    record = {"completed": [], "uncompleted": []}
    for kw in keywords:
        print("uncompleted: ", record.get("uncompleted"))
        process(sess, kw, record)

    return record




