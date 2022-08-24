import requests
import os

from pathlib import Path
from bs4 import BeautifulSoup
from pathvalidate import sanitize_filename


def check_for_redirect(response):
    if response.history:
        raise requests.TooManyRedirects

def download_txt(response, filename, folder='books/', number=None):
    checked_filename = sanitize_filename(filename)
    checked_folder = sanitize_filename(folder)
    Path(checked_folder).mkdir(parents=True, exist_ok=True)
    with open(f'{checked_folder}/{number} {checked_filename}.txt', 'w', encoding='UTF-8') as file:
        file.write(response.text)
    return os.path.join(checked_folder, f'{checked_filename}.txt')

for i in range(10):
    text_url = f'https://tululu.org/txt.php?id={i+1}'
    text_response = requests.get(text_url)
    try:
        check_for_redirect(text_response)

        title_url = f'https://tululu.org/b{i+1}/'
        title_response = requests.get(title_url)
        soup = BeautifulSoup(title_response.text, 'lxml')
        book_name = soup.find('table').find('h1').text
        title_name = book_name.split('::')[0].strip()
        download_txt(response=text_response, filename=title_name, folder='books', number=i+1)
    except requests.TooManyRedirects:
        pass




