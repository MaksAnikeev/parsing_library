import requests
import os

from pathlib import Path
from bs4 import BeautifulSoup
from pathvalidate import sanitize_filename
from urllib.parse import urljoin


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

def download_image(url, filename, folder='image/'):
    checked_filename = sanitize_filename(filename)
    checked_folder = sanitize_filename(folder)
    Path(checked_folder).mkdir(parents=True, exist_ok=True)
    response = requests.get(url)
    with open(f'{checked_folder}/{checked_filename}', 'wb') as file:
        file.write(response.content)
    return os.path.join(checked_folder, f'{checked_filename}')

list=[4]
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
        # download_txt(response=text_response, filename=title_name, folder='books', number=i+1)

        # image_link = soup.find(class_='bookimage').find('img')['src']
        # full_image_link = urljoin('https://tululu.org/', image_link)
        # image_name = image_link.split('/')[-1]
        # download_image(url=full_image_link, filename=image_name, folder='image/')

        # print(title_name)
        # comments = soup.find(class_='ow_px_td').find_all(class_='black')
        # for comment in comments:
        #     print(comment.text)
        # print()

        print(title_name)
        book_genres = soup.find('span', class_='d_book').find_all('a')
        genres = []
        for genre in book_genres:
            genres.append(genre.text)
        print(genres, '\n')




    except requests.TooManyRedirects:
        pass




