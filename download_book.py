import argparse
import os
from pathlib import Path
from urllib.parse import urljoin


import requests
from bs4 import BeautifulSoup
from pathvalidate import sanitize_filename
from parsing_library import check_for_redirect

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


def download_book(folder, number):
    title_url = f'https://tululu.org/b{number}/'
    title_response = requests.get(title_url)
    soup = BeautifulSoup(title_response.text, 'lxml')
    image_link = soup.find(class_='bookimage').find('img')['src']
    full_image_link = urljoin('https://tululu.org/', image_link)
    book_name = soup.find('table').find('h1').text
    title_name = book_name.split('::')[0].strip()
    download_image(url=full_image_link,
                   filename=title_name,
                   folder=folder)

    text_url = f'https://tululu.org/txt.php?id={number}'
    text_response = requests.get(text_url)
    download_txt(response=text_response,
                 filename=title_name,
                 folder=folder)


def download_books(folder):
    choise = int(input('Напишите 1, если вы хотите скачать книги диапозоном или 2 если по номерам: '))
    if choise == 1:
        books_range = input('Введите номера книги c которого начать и которым закончить скачивание, через запятую: ')
        start, stop = books_range.split(',')
        for number in range(int(start), int(stop)+1):
            text_url = f'https://tululu.org/txt.php?id={number}'
            text_response = requests.get(text_url)
            try:
                check_for_redirect(text_response)
                download_book(folder, number)
            except:
                pass
    elif choise == 2:
        numbers = input('Введите номера через запятую: ')
        for number in numbers.split(','):
            download_book(folder, number=int(number))
    else:
        print('Вы ввели не правильную цифру')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('folder',
                        nargs='?',
                        help='папка для скачивания книг, по умолчанию books',
                        default='books')
    args = parser.parse_args()

    download_books(folder=args.folder)
