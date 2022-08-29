import argparse
import time

import requests
from bs4 import BeautifulSoup


def check_for_redirect(response):
    if response.history:
        raise requests.TooManyRedirects


def parse_book_page(response):
    soup = BeautifulSoup(response.text, 'lxml')
    title_name, aurhor = soup.find('table').find('h1').text.split('::')

    book_genres = soup.find('span', class_='d_book').find_all('a')
    genres = [genre.text for genre in book_genres]

    book_comments = soup.find(class_='ow_px_td').find_all(class_='black')
    comments = [comment.text for comment in book_comments]

    return title_name.strip(), aurhor.strip(), genres, comments


def parse_tululu(number):
    text_url = 'https://tululu.org/txt.php'
    payload = {'id': number}
    text_response = requests.get(text_url, params=payload)
    text_response.raise_for_status()
    check_for_redirect(text_response)

    book_url = f'https://tululu.org/b{number}/'
    book_response = requests.get(book_url)
    book_response.raise_for_status()
    check_for_redirect(book_response)

    return book_response


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('start_id',
                        type=int,
                        help='номер с которого начать')
    parser.add_argument('end_id',
                        type=int,
                        help='номер которым закончить')
    args = parser.parse_args()

    for number in range(args.start_id, args.end_id + 1):
        try:
            title_name, aurhor, genres, comments = parse_book_page(response=parse_tululu(number))
            print(number, ' Название: ', title_name, '.', ' Автор: ', aurhor, '.', sep='')
            print(genres)
            print('Комментарии:')
            for comment in comments:
                print(comment)
            print()

        except requests.TooManyRedirects:
            print(f'Oops. Книги под номером {number} не существует', '\n')
        except requests.exceptions.HTTPError as err:
            code = err.response.status_code
            print(f'Oops. При поиски книги номер {number} возникла ошибка {code}')
            print(f'Response is: {err.response.content}', '\n')
        except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
            print('Oops. Ошибка соединения. Проверьте интернет связь')
            time.sleep(20)






