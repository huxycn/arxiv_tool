import requests

from loguru import logger
from pathlib import Path
from tqdm import tqdm
from tenacity import retry, stop_after_attempt


HEADERS = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:27.0) Gecko/20100101 Firefox/27.0'}


class PdfDownloader:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers = HEADERS

    def set_proxy(self, proxy=None):
        if proxy:
            self.sess.proxies = {"http": proxy, "https": proxy, }

    @retry(stop=stop_after_attempt(3))
    def download(self, url, path, auth=None):
        if Path(path).exists():
            logger.warning(f'PDF {path} already exists, skip downloading!')
            return True
        try:
            logger.info(f'Downloading {url} to {path}')
            response = self.session.get(url, auth=auth, stream="TRUE")

            if response.headers["Content-Type"] != "application/pdf":
                logger.warning(f'Failed to fetch pdf with url: {url}, retry ...')
                raise Exception("Failed to fetch pdf with url: {url}")
            else:
                total = int(response.headers.get('content-length'))
                with open(path, 'wb') as file:
                    for data in tqdm(response.iter_content(), total=total, unit='B', unit_scale=True, unit_divisor=1024):
                        file.write(data)
                return True
        except:
            logger.warning(f'Failed to open url: {url}, retry ...')
            raise Exception("Failed to open url: {url}")


if __name__ == "__main__":
    pdf_downloader = PdfDownloader()
    pdf_downloader.download("http://arxiv.org/pdf/1706.03762v7", "test.pdf")
