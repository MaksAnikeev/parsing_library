import argparse
import os
from pathlib import Path
import time
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup
from pathvalidate import sanitize_filename
from parsing_library import check_for_redirect


def download_txt(number, filename, folder='books/'):
    text_url = f'https://tululu.org/txt.php'
    payload = {'id': number}
    text_response = requests.get(text_url, params=payload)
    text_response.raise_for_status()
    checked_filename = sanitize_filename(filename)
    checked_folder = sanitize_filename(folder)
    Path(checked_folder).mkdir(parents=True,
                               exist_ok=True)
    with open(os.path.join(checked_folder, f'{checked_filename}.txt'), 'w', encoding='UTF-8') as file:
        file.write(text_response.text)
    return os.path.join(checked_folder, f'{checked_filename}.txt')


def download_image(url, filename, folder='image/'):
    checked_filename = sanitize_filename(filename)
    checked_folder = sanitize_filename(folder)
    Path(checked_folder).mkdir(parents=True,
                               exist_ok=True)
    response = requests.get(url)
    with open(os.path.join(checked_folder, f'{checked_filename}.jpg'), 'wb') as file:
        file.write(response.content)
    return os.path.join(checked_folder, f'{checked_filename}')


def download_book(folder, number):
    book_url = f'https://tululu.org/b{number}/'
    book_response = requests.get(book_url)
    book_response.raise_for_status()
    soup = BeautifulSoup(book_response.text, 'lxml')
    image_link = soup.find(class_='bookimage').find('img')['src']
    full_image_link = urljoin('https://tululu.org', image_link)
    book_name = soup.find('table').find('h1').text
    title_name = book_name.split('::')[0].strip()
    download_image(url=full_image_link,
                   filename=title_name,
                   folder=folder)

    download_txt(number=number,
                 filename=title_name,
                 folder=folder)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('folder',
                        nargs='?',
                        help='папка для скачивания книг, по умолчанию books',
                        default='books')
    args = parser.parse_args()

    choise = int(input('Напишите 1, если вы хотите скачать книги диапозоном или 2 если по номерам: '))
    if choise == 1:
        books_range = input('Введите номера книги c которого начать и которым закончить скачивание, через запятую: ')
        start, stop = books_range.split(',')
        for number in range(int(start), int(stop) + 1):
            try:
                text_url = f'https://tululu.org/txt.php?id={number}'
                text_response = requests.get(text_url)
                text_response.raise_for_status()
                check_for_redirect(text_response)
                download_book(args.folder, number)
            except requests.TooManyRedirects:
                print(f'Oops. Книги под номером {number} не существует')
                pass
            except requests.exceptions.HTTPError as err:
                code = err.response.status_code
                print(f'Oops. При поиски книги номер {number} возникла ошибка {code}')
                print(f'Response is: {err.response.content}')
                pass
            except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
                print('Oops. Ошибка соединения. Проверьте интернет связь')
                time.sleep(20)
                pass

    elif choise == 2:
        numbers = input('Введите номера через запятую: ')
        for number in numbers.split(','):
            try:
                download_book(args.folder, number=int(number))
            except requests.TooManyRedirects:
                print(f'Oops. Книги под номером {number} не существует')
                pass
            except requests.exceptions.HTTPError as err:
                code = err.response.status_code
                print(f'Oops. При поиски книги номер {number} возникла ошибка {code}')
                print(f'Response is: {err.response.content}')
                pass
            except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
                print('Oops. Ошибка соединения. Проверьте интернет связь')
                time.sleep(20)
                pass
    else:
        print('Вы ввели не правильную цифру')
