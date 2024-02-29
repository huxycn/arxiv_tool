import sys
import fire

from pathlib import Path
from loguru import logger

from .core.arxiv_api import ArxivApi
from .core.pattern_recognizer import PatternRecognizer
from .core.pdf_downloader import PdfDownloader


def get_pdf_name(arxiv_info, paper_alias=''):
    _id = arxiv_info['id']
    title = paper_alias if paper_alias else arxiv_info['title'].replace(' ', '_')
    author = arxiv_info['author'][0].replace(' ', '_') + '_et_al'
    pdf_name = f'{title}_{author}_{_id}.pdf'
    return pdf_name


def get_paper_info(arxiv_info):
    title = arxiv_info['title']
    author = arxiv_info['author'][0] + ' et al'
    year = arxiv_info['published'].split('-')[0]

    paper_info = f'**{title}**. {author}. {year}.'
    return paper_info


def download_from_url(arxiv_url, output_pdf_dir='./pdfs'):
    arxiv_api = ArxivApi()
    pdf_downloader = PdfDownloader()

    arxiv_id = arxiv_url.split('/')[-1]

    arxiv_info = arxiv_api.fetch_arxiv_info(arxiv_id)

    pdf_link = arxiv_info['pdf']

    pdf_path = Path(output_pdf_dir) / get_pdf_name(arxiv_info)

    pdf_downloader.download(pdf_link, pdf_path)


def get_md_files(md_file_or_dir):
    if Path(md_file_or_dir).is_dir():
        md_files = list(Path(md_file_or_dir).rglob('*.md'))
    elif Path(md_file_or_dir).is_file() and Path(md_file_or_dir).suffix == '.md':
        md_files = [Path(md_file_or_dir)]
    else:
        md_files = []
    return md_files


def download_from_md_and_update(md_file_or_dir, output_pdf_dir='./pdfs'):
    arxiv_api = ArxivApi()
    pattern_recognizer = PatternRecognizer(r'- (.*)({{https://arxiv.org/abs/\d{4}.\d{5}}})')
    pattern_recognizer_replace = PatternRecognizer(r'{{https://arxiv.org/abs/\d{4}.\d{5}}}')
    pdf_downloader = PdfDownloader()

    md_files = get_md_files(md_file_or_dir)
    logger.info('# ' + '='*50)
    logger.info('# ' + f'Start to process {md_file_or_dir}')
    logger.info('# ' + f'Find {len(md_files)} markdown files:')
    for md_idx, md_file in enumerate(md_files):
        logger.info('# ' + f'    {md_idx+1}. {md_file}')
    logger.info('# ' + '='*50)
    logger.info('')

    for md_idx, md_file in enumerate(md_files):
        with open(md_file, 'r') as f:
            content = f.read()

        replace_dict = {}
        arxiv_urls = pattern_recognizer.findall(content)
        logger.info(f'==> [{md_idx+1}/{len(md_files)}] processing markdown file: {md_file} ({len(arxiv_urls)} urls) ...')
        for url_idx, arxiv_url in enumerate(arxiv_urls):
            try:
                logger.info(f'    --> ({url_idx+1}/{len(arxiv_urls)}) processing arxiv url: {arxiv_url} ...')
                paper_alias = arxiv_url[0].strip().replace(':', '')
                arxiv_url_with_braces = arxiv_url[1]
                arxiv_url = arxiv_url_with_braces[2:-2]
                arxiv_id = arxiv_url.split('/')[-1]
                arxiv_info = arxiv_api.fetch_arxiv_info(arxiv_id)
                pdf_link = arxiv_info['pdf']
                pdf_path = Path(output_pdf_dir) / get_pdf_name(arxiv_info, paper_alias)
                pdf_path.parent.mkdir(parents=True, exist_ok=True)

                pdf_downloader.download(pdf_link, pdf_path)

                replace_dict[arxiv_url_with_braces] = f'{get_paper_info(arxiv_info)} [arxiv]({arxiv_url}) [pdf]({pdf_path})'
            except Exception as e:
                logger.warning(f'{arxiv_url} failed: {e}')
        
        replaced_content = pattern_recognizer_replace.multiple_replace(content, **replace_dict)
        with open(md_file, 'w') as f:
            f.write(replaced_content)
        logger.info(f'==> [{md_idx+1}/{len(md_files)}] markdown file {md_file} updated!')


def main():
    logger.remove()
    logger.add(
        sys.stdout,
        level='INFO',
    )
    fire.Fire({
        'fetch': download_from_url,
        'sync': download_from_md_and_update,
    })
