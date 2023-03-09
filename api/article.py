"""create api and when it is hit, it creates articles with the data passed into it"""

import sys
from typing import List

import jinja2
import requests
from requests.auth import HTTPBasicAuth
from requests import ReadTimeout, ConnectionError, RequestException

from config import APPLICATION_PASSWORD, CATEGORY_ID, USERNAME, SITE_URL

WP_URL = f"{SITE_URL}/wp-json/wp/v2"

headers = {"Accept": "application/json", "Content-Type": "application/json"}
auth = HTTPBasicAuth(USERNAME, APPLICATION_PASSWORD)
environment = jinja2.Environment()
template = environment.from_string("""
{% for link in links %}
<article>
    <div>
        <img src="{{ link.get('thumbnail') }}" alt="{{ link.get('title') }}" width=\"320\" height=\"180\">
    </div>
    <div>
        <h3>{{ link.get('title') }}</h3>
        <div>
            <span><button class="play-video" data-video-id="{{ link.get('id') }}" style="margin-right: 10px;">Play Video</button></span>
            <button class="download-video" data-video-id="{{ link.get('id') }}">Download Video</button>
        </div>
    </div>
    <br><hr>
    <div class="iframe-container" data-video-id="{{ link.get('id') }}"></div>
</article>
{% endfor %}

<script>
    //<![CDATA[
    const playButtons = document.querySelectorAll('.play-video');
    const downloadButtons = document.querySelectorAll('.download-video');
    const iframeContainers = document.querySelectorAll('.iframe-container');

    playButtons.forEach(button => {
        button.addEventListener('click', () => {
            const videoId = button.dataset.videoId;
            const iframeContainer = document.querySelector(`.iframe-container[data-video-id="${videoId}"]`);
            iframeContainer.innerHTML = `<iframe src="https://www.youtube.com/embed/${videoId}" height="500" width="700"></iframe>`;
        });
    });

    downloadButtons.forEach(button => {
        button.addEventListener('click', () => {
            const videoId = button.dataset.videoId;
            window.open(`https://s.shabakngy.com/go/g.php?q=${videoId}`, '_blank');
        });
    });
    //]]>
</script>

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

def current_keywords_posted() -> list:
    per_page = 100
    page = 1
    keywords = []

    while True:
        # Make a request to the WordPress REST API to retrieve posts in the category
        url = f"{SITE_URL}/wp-json/wp/v2/posts?categories={CATEGORY_ID}&per_page={per_page}&page={page}"
        try:
            response = requests.get(url)
            response_posts = response.json()
            # If there are no more posts, break out of the loop
            if not response_posts or response.status_code != 200:
                break

            # Append the posts to the list of posts
            keywords += [i["title"]["rendered"] for i in response_posts]

            # Increment the page number for the next request
            page += 1

        except ReadTimeout:
            break

        except RequestException as e:
            print(e)
            break

    return keywords



