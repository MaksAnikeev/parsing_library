import argparse
import os
from pathlib import Path
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup
from pathvalidate import sanitize_filename


def check_for_redirect(response):
    if response.history:
        raise requests.TooManyRedirects


def download_txt(response, filename, folder='books/'):
    checked_filename = sanitize_filename(filename)
    checked_folder = sanitize_filename(folder)
    Path(checked_folder).mkdir(parents=True,
                               exist_ok=True)
    with open(f'{checked_folder}/{checked_filename}.txt', 'w', encoding='UTF-8') as file:
        file.write(response.text)
    return os.path.join(checked_folder, f'{checked_filename}.txt')


def download_image(url, filename, folder='image/'):
    checked_filename = sanitize_filename(filename)
    checked_folder = sanitize_filename(folder)
    Path(checked_folder).mkdir(parents=True,
                               exist_ok=True)
    response = requests.get(url)
    with open(f'{checked_folder}/{checked_filename}.jpg', 'wb') as file:
        file.write(response.content)
    return os.path.join(checked_folder, f'{checked_filename}')


def parse_book_page(response, number):
    soup = BeautifulSoup(response.text, 'lxml')
    book_name = soup.find('table').find('h1').text
    title_name = book_name.split('::')[0].strip()
    aurhor = book_name.split('::')[1].strip()
    print(number, ' Название: ', title_name, '.', ' Автор: ', aurhor, '.', sep='')

    book_genres = soup.find('span', class_='d_book').find_all('a')
    genres = []
    for genre in book_genres:
        genres.append(genre.text)
    print(genres)

    comments = soup.find(class_='ow_px_td').find_all(class_='black')
    print('Комментарии:')
    for comment in comments:
        print(comment.text)
    print()


def parse_tululu(start_id, end_id):
    for i in range(start_id, end_id + 1):
        text_url = f'https://tululu.org/txt.php?id={i}'
        text_response = requests.get(text_url)
        try:
            check_for_redirect(text_response)

            title_url = f'https://tululu.org/b{i}/'
            title_response = requests.get(title_url)

            parse_book_page(response=title_response,
                            number=i)
        except requests.TooManyRedirects:
            pass


def download_books(folder='books'):
    numbers = input('Введите номера через запятую: ')
    for i in numbers.split(','):
        title_url = f'https://tululu.org/b{i.strip()}/'
        title_response = requests.get(title_url)
        soup = BeautifulSoup(title_response.text, 'lxml')
        image_link = soup.find(class_='bookimage').find('img')['src']
        full_image_link = urljoin('https://tululu.org/', image_link)
        book_name = soup.find('table').find('h1').text
        title_name = book_name.split('::')[0].strip()
        download_image(url=full_image_link,
                       filename=title_name,
                       folder=folder)

        text_url = f'https://tululu.org/txt.php?id={i.strip()}'
        text_response = requests.get(text_url)
        download_txt(response=text_response,
                     filename=title_name,
                     folder=folder)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('start_id',
                        type=int,
                        help='номер с которого начать')
    parser.add_argument('end_id',
                        type=int,
                        help='номер которым закончить')
    args = parser.parse_args()

    parse_tululu(start_id=args.start_id,
                 end_id=args.end_id)
