"""create api and when it is hit, it creates articles with the data passed into it"""
import sys
from typing import List

import jinja2
from requests.auth import HTTPBasicAuth
from requests import ReadTimeout, ConnectionError

from config import APPLICATION_PASSWORD, CATEGORY_ID, USERNAME, SITE_URL

APPLICATION_PASSWORD_TEST = "9lkj Vuq7 FvCY ygGH aRlX sKkW"
USERNAME_TEST = "root"

SITE_URL_TEST = "http://hello-world/"
WP_URL = f"{SITE_URL}/wp-json/wp/v2"

headers = {"Accept": "application/json", "Content-Type": "application/json"}
auth = HTTPBasicAuth(USERNAME, APPLICATION_PASSWORD)
environment = jinja2.Environment()
template = environment.from_string("""
    <h1>{{ query }}</h1>
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
        print(title)
        res = client.post(WP_URL + '/posts', auth=auth, headers=headers, json=data, timeout=20)
        if res.status_code == 201:
            return True

    except ReadTimeout as e:
        print(f"error posting article {title}:", e)
        return None
    except ConnectionError as e:
        print("no internet!", e)
        sys.exit()




