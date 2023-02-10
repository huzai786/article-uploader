"""create api and when it is hit, it creates articles with the data passed into it"""
import sys
from typing import List

import jinja2
from requests.auth import HTTPBasicAuth
from requests import ReadTimeout, ConnectionError, RequestException

from config import APPLICATION_PASSWORD, CATEGORY_ID, USERNAME, SITE_URL

WP_URL = f"{SITE_URL}/wp-json/wp/v2"

if CATEGORY_ID == "":
    CATEGORY_ID = []
else:
    CATEGORY_ID = int(CATEGORY_ID)

headers = {"Accept": "application/json", "Content-Type": "application/json"}
auth = HTTPBasicAuth(USERNAME, APPLICATION_PASSWORD)
environment = jinja2.Environment()
template = environment.from_string("""
    {% for link in links %}
        <article>
            <div>
            <img src="{{ link.get('thumbnail') }}" alt="{{ link.get('title') }}" width=\"320\" height=\"180\">
            </div>
            <h3>{{ link.get('title') }}</h3>
            <button onclick="get_{{ loop.index }}()" style="margin-bottom: 15px;">Play Video</button>
            <br><hr>
            <script>
                function get_{{ loop.index }}() {
                    document.getElementById("iframe{{ link.get('id')}}").innerHTML =
                     `<iframe src=https://www.youtube.com/embed/{{ link.get('id') }} height="500" 
                     width="700"></iframe>`;
                }
            </script>
            <div id=iframe{{ link.get('id') }}></div>
            
        </article>
    {% endfor %}
""")

def html_format_data(links: List[dict], query: str):
    html = template.render(links=links, query=query)
    return html

def add_article(title: str, content: str, client):
    try:
        data = {
            "name": title,
            "slug": title,
            "title": title,
            "status": 'publish',
            "content": content,
            "excerpt": content,
            "format": "standard",
            "categories": CATEGORY_ID,
        }
        res = client.post(WP_URL + '/posts', auth=auth, headers=headers, json=data, timeout=20)
        if res.status_code == 201:
            return True

    except ReadTimeout as e:
        print(f"error posting article {title}:", e)
        return None
    except ConnectionError as e:
        print("no internet!", e)
        sys.exit()

def get_last_kw(client):
    try:
        data = {}
        if CATEGORY_ID:
            data["categories"] = CATEGORY_ID

        res = client.get(WP_URL + '/posts', auth=auth, headers=headers, timeout=20, json=data)
        if res.status_code == 200:
            if isinstance(res.json(), list) and len(res.json()) > 0:
                title = res.json()[0]["title"]["rendered"]
                print("Last Article Keyword: ", title)
                return title
            else:
                return None

    except ReadTimeout:
        return None

    except RequestException as e:
        print(e)
        return None

