import argparse
import time

import requests
from bs4 import BeautifulSoup
from pathvalidate import sanitize_filename
from urllib.parse import urljoin


def check_for_redirect(response):
    if response.history:
        raise requests.TooManyRedirects


def parse_book_page(response, book_url):
    soup = BeautifulSoup(response.text, 'lxml')

    book_name, author = soup.select('table h1')[0].text.split('::')
    title_name = sanitize_filename(book_name.replace('.', '!'))

    book_genres = soup.select('span.d_book a')
    genres = [genre.text for genre in book_genres]

    book_comments = soup.select('.ow_px_td .black')
    comments = [comment.text for comment in book_comments]

    image_link_list = soup.select(".bookimage img[src]")
    image_link = image_link_list[0]['src']
    full_image_link = urljoin(book_url, image_link)

    return title_name.strip(), author.strip(), genres, comments, full_image_link


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
            text_url = 'https://tululu.org/txt.php'
            payload = {'id': number}
            text_response = requests.get(text_url, params=payload)
            text_response.raise_for_status()
            check_for_redirect(text_response)

            book_url = f'https://tululu.org/b{number}/'
            book_response = requests.get(book_url)
            book_response.raise_for_status()
            check_for_redirect(book_response)
            title_name, author, genres, comments, full_image_link = parse_book_page(response=book_response,
                                                                                    book_url=book_url)
            print(number, ' Название: ', title_name, '.', ' Автор: ', author, '.', sep='')
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
