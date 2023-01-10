import re
import json
import time
from urllib.parse import quote

import requests
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
from youtubesearchpython import VideosSearch


ua = UserAgent()
sess = requests.Session()

def __get_html(query):

    headers = {
        'User-Agent': ua.random,
    }
    try:
        r = sess.get(f'https://www.youtube.com/results?search_query={quote(query)}', headers=headers)
        r.raise_for_status()
        return r.text

    except requests.RequestException as e:
        print(e)
        raise SystemExit(f'Error: {e}')


def __get_js_script(data):
    bs = BeautifulSoup(data, 'lxml')

    try:
        script_tags = bs.find("script", text=re.compile('responseContext'))
        return script_tags.text

    except AttributeError as e:
        print(e)
        return


def __extract_json(data):
    python_str = re.sub("var ytInitialData = ", "", data, 1)
    main_part = python_str.rsplit('}', 1)[0] + "}"
    try:
        obj = json.loads(main_part)
        return obj

    except json.decoder.JSONDecodeError as e:
        raise e


def __scrape_youtube(python_dict):
    links = []
    try:
        links_json = python_dict["contents"]["twoColumnSearchResultsRenderer"]["primaryContents"][
            "sectionListRenderer"]["contents"][0]["itemSectionRenderer"]["contents"]
        for l in links_json:
            if "videoRenderer" in l.keys():
                _id = l["videoRenderer"].get("videoId")
                thumbnail = l["videoRenderer"]['thumbnail']['thumbnails'][0]['url']
                title = l["videoRenderer"]['title']['runs'][0]["text"]
                data = {"id": _id, "thumbnail": thumbnail, "title": title}
                links.append(data)

    except TypeError as e:
        print(e)

    return links

def extract_youtube(query: str):
    html = __get_html(query)
    retries = 0
    while retries < 3:
        time.sleep(0.4)
        js_string = __get_js_script(html)
        if not js_string:
            retries += 1
            continue
        try:
            python_dict = __extract_json(js_string)
            return __scrape_youtube(python_dict)

        except json.decoder.JSONDecodeError:
            retries += 1
            continue

    return get_from_lib(query)


def get_from_lib(query):
    videosSearch = VideosSearch(query)
    links = []
    for i in videosSearch.result().get("result"):
        if i.get("type") == 'video':
            try:
                _id = i.get("id")
                thumbnail = i.get("richThumbnail").get("url")
                title = i.get('title')
                data = {"id": _id, "thumbnail": thumbnail, "title": title}
                links.append(data)

            except AttributeError:
                pass

    return links

