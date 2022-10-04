import argparse
import os
from pathlib import Path
import time
import json

import requests
from pathvalidate import sanitize_filename
from parsing_library import check_for_redirect, parse_book_page
from parse_tululu_category import parse_category_page


def download_txt(number, filename, folder='books/'):
    text_url = f'https://tululu.org/txt.php'
    payload = {'id': number}
    text_response = requests.get(text_url, params=payload)
    text_response.raise_for_status()
    checked_filename = sanitize_filename(filename)
    checked_folder = sanitize_filename(folder)
    Path(checked_folder).mkdir(parents=True,
                               exist_ok=True)
    file_path = os.path.join(checked_folder, f'{checked_filename}.txt')
    with open(file_path, 'w', encoding='UTF-8') as file:
        file.write(text_response.text)
    return file_path


def download_image(url, filename, folder='image/'):
    checked_filename = sanitize_filename(filename)
    checked_folder = sanitize_filename(folder)
    Path(checked_folder).mkdir(parents=True,
                               exist_ok=True)
    response = requests.get(url)
    file_path = os.path.join(checked_folder, f'{checked_filename}.jpg')
    with open(file_path, 'wb') as file:
        file.write(response.content)
    return file_path


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('folder',
                        nargs='?',
                        help='папка для скачивания книг, по умолчанию books',
                        default='books')
    args = parser.parse_args()

    choise = int(input('''Напишите
    1 - если вы хотите скачать книги диапозоном
    2 - если вы хотите скачать книги по номерам
    3 - если вы хотите скачать все книги с категории
    : '''))
    if choise == 1:
        books_range_input = input(
            'Введите номера книги c которого начать и которым закончить скачивание, через запятую: ')
        start, stop = books_range_input.split(',')
        books_range = [book for book in range(int(start), int(stop) + 1)]
    elif choise == 2:
        numbers = input('Введите номера через запятую: ')
        books_range = numbers.split(',')
    elif choise == 3:
        category_url = input('''Введите url адрес сайта с категорией. Пример - https://tululu.org/l55/
        : ''')
        pages_quantity = int(input('Введите количество страниц для скачивания: '))
        print('Загружаем книги с выбранной категории. Подождите.')
        books_range = []
        for number in range(pages_quantity+1):
            category_response = requests.get(f'{category_url}{number}/')
            category_response.raise_for_status()
            one_page_books_range = parse_category_page(category_response)
            books_range.extend(one_page_books_range)
    else:
        print('Вы ввели не правильную цифру')

    books_json = []
    for number in books_range:
        try:
            book_url = f'https://tululu.org/b{int(number)}/'
            book_response = requests.get(book_url)
            book_response.raise_for_status()
            check_for_redirect(book_response)

            title_name, author, genres, comments, full_image_link = parse_book_page(response=book_response,
                                                                                    book_url=book_url)
            book_params = {
                'title': title_name,
                'author': author,
                'img_scr': f'{args.folder}/{title_name}.jpg',
                'book_path': f'{args.folder}/{title_name}.txt',
                'comments': comments,
                'genres': genres
            }
            books_json.append(book_params)

            download_image(url=full_image_link,
                           filename=title_name,
                           folder=args.folder)

            download_txt(number=number,
                         filename=title_name,
                         folder=args.folder)
        except requests.TooManyRedirects:
            print(f'Oops. Книги под номером {number} не существует')
        except requests.exceptions.HTTPError as err:
            code = err.response.status_code
            print(f'Oops. При поиски книги номер {number} возникла ошибка {code}')
            print(f'Response is: {err.response.content}')
        except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
            print('Oops. Ошибка соединения. Проверьте интернет связь')
            time.sleep(20)

    with open('books_json.json', 'w', encoding='utf8') as json_file:
        json.dump(books_json, json_file, ensure_ascii=False)
