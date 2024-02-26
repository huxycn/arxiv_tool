import sys
import feedparser

from loguru import logger
from tabulate import tabulate
from unidecode import unidecode
from urllib.request import ProxyHandler
from tenacity import retry, stop_after_attempt

try:
    from urllib import quote
except ImportError:
    from urllib.parse import quote


HEADERS = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:27.0) Gecko/20100101 Firefox/27.0'}


class ArxivApi:
    def __init__(self):
        self.base_url = "http://export.arxiv.org/api/query"

    def set_proxy_handler(self, proxy):
        proxy_handler = ProxyHandler({"http": f"http://{proxy}", "https": f"https://{proxy}"})
        return proxy_handler

    def extract_json_info(self, item):
        updated = item.updated.split("T")[0]
        published = item.published.split("T")[0]
        title = item.title.strip().replace('\n', '')
        authors = [author["name"] for author in item.authors]
        url = item.links[0].href
        pdf = item.links[1].href

        info_dict = {
            "id": item.id,
            "updated": updated,
            "published": published,
            "title": title,
            "author": authors,
            "journal": "arxiv",
            "url": url,
            "pdf": pdf
        }

        info_msg = f'{", ".join([f"{key}: {value}" for key, value in info_dict.items()])}'

        logger.debug(f'extract arxiv info: {info_msg}')
        return info_dict

    @retry(stop=stop_after_attempt(3))
    def fetch_arxiv_info(self, _id, handler=False):
        params = "?search_query=id:"+quote(unidecode(_id))

        logger.debug(f'fetching arxiv info with id: {_id} ...')
        try:
            if handler:
                result = feedparser.parse(self.base_url + params, handlers=[handler], request_headers=HEADERS)
            else:
                result = feedparser.parse(self.base_url  + params, request_headers=HEADERS)
            items = result.entries
            item = items[0]
            item['id'] = _id
            logger.debug(f'fetch arxiv info: {item}')
            return self.extract_json_info(item)
        except Exception as e:
            logger.error(f'fetching arxiv info failed: {e}')
            raise Exception(f'fetching arxiv info failed: {e}')


if __name__ == "__main__":
    logger.remove()
    logger.add(sys.stdout, level="INFO")
    arxiv_api = ArxivApi()
    arxiv_info = arxiv_api.fetch_arxiv_info('1706.03762')
