import requests

from loguru import logger
from tenacity import retry, stop_after_attempt


HEADERS = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:27.0) Gecko/20100101 Firefox/27.0'}


class PdfDownloader:
    def __init__(self):
        self.sess = requests.Session()
        self.sess.headers = HEADERS

    def set_proxy(self, proxy=None):
        if proxy:
            self.sess.proxies = {"http": proxy, "https": proxy, }

    @retry(stop=stop_after_attempt(3))
    def download(self, url, path, auth=None):
        try:
            logger.info(f'fetching pdf conent with link: {url} ...')
            r = self.sess.get(url, auth=auth)

            if r.headers["Content-Type"] != "application/pdf":
                logger.warning('Failed to fetch pdf with url: {url}, retry ...')
                raise Exception("Failed to fetch pdf with url: {url}")
            else:
                with open(path, "wb") as f:
                    f.write(r.content)
                logger.info(f"download {url} as {path}")
                return True
        except:
            logger.warning('Failed to open url: {url}, retry ...')
            raise Exception("Failed to open url: {url}")


if __name__ == "__main__":
    pdf_downloader = PdfDownloader()
    pdf_downloader.download("http://arxiv.org/pdf/1706.03762v7", "test.pdf")
