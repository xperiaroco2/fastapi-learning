from concurrent.futures import ThreadPoolExecutor

import requests
from bs4 import BeautifulSoup
from pathlib import Path


Path('data/raw').mkdir(parents=True, exist_ok=True)
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}


def download_pdf(content_page_url: str):
    print(f"Downloading PDF from {content_page_url}")

    response = requests.get(content_page_url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')

    articles = soup.select('h1.article__title-name')
    download_buttons = soup.select('button.article__button-download-button')

    if not download_buttons or not articles:
        print(f"No content at {content_page_url}")
        return

    href = download_buttons[0].attrs['onclick'].split('location.href=')[-1].replace('\'', '')

    file_response = requests.get(href)
    filename = articles[0].text[:70]
    filename = filename.replace('/', '_').replace(':', '')

    with open(f"data/raw/{filename}.pdf", "wb") as file:
        print(f"Writing file {filename}.pdf")
        file.write(file_response.content)


def download_pdfs_from_list(list_page_url: str) -> bool:
    list_page_response = requests.get(list_page_url, headers=headers)
    list_page = BeautifulSoup(list_page_response.text, 'html.parser')

    links = list_page.select('a.publications-by-topic__link-name')

    if not links:
        return False

    def handle_download_pdf(link):
        url = link.get('href')
        url = f"https://osvita.ua{url}"

        try:
            download_pdf(url)
        except Exception as exc:
            print(exc)

    with ThreadPoolExecutor(max_workers=8) as executor:
        executor.map(handle_download_pdf, links)

    return True



pagination = 0

while True:
    next_url = f'https://osvita.ua/legislation/list/{pagination}'

    print(f"Move to the next 20 items at {next_url}")

    try:
        has_more = download_pdfs_from_list(next_url)

        if not has_more:
            break
    except Exception as exc:
        print(exc)
        break

    pagination += 20






