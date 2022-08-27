import argparse
import time

import requests
from bs4 import BeautifulSoup


def check_for_redirect(response):
    if response.history:
        raise requests.TooManyRedirects


def parse_book_page(response, number):
    soup = BeautifulSoup(response.text, 'lxml')
    book_name = soup.find('table').find('h1').text
    title_name, aurhor = book_name.split('::')
    print(number, ' Название: ', title_name.strip(), '.', ' Автор: ', aurhor.strip(), '.', sep='')

    book_genres = soup.find('span', class_='d_book').find_all('a')
    genres = [genre.text for genre in book_genres]
    print(genres)

    comments = soup.find(class_='ow_px_td').find_all(class_='black')
    print('Комментарии:')
    for comment in comments:
        print(comment.text)
    print()


def parse_tululu(start_id, end_id):
    for number in range(start_id, end_id + 1):
        try:
            text_url = 'https://tululu.org/txt.php'
            payload = {'id': number}
            text_response = requests.get(text_url, params=payload)
            text_response.raise_for_status()
            check_for_redirect(text_response)

            title_url = f'https://tululu.org/b{number}/'
            title_response = requests.get(title_url)
            title_response.raise_for_status()

            parse_book_page(response=title_response,
                            number=number)
        except requests.TooManyRedirects:
            print(f'Oops. Книги под номером {number} не существует')
            pass
        except requests.exceptions.HTTPError as err:
            code = err.response.status_code
            print(f'Oops. При поиски книги номер {number} возникла ошибка {code}')
            print(f'Response is: {err.response.content}')
            pass


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('start_id',
                        type=int,
                        help='номер с которого начать')
    parser.add_argument('end_id',
                        type=int,
                        help='номер которым закончить')
    args = parser.parse_args()

    patience = 10
    while True:
        try:
            parse_tululu(start_id=args.start_id,
                     end_id=args.end_id)
            break
        except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
            print('Oops. Ошибка соединения. Проверьте интернет связь')
            patience -= 1
            if not patience:
                break
            else:
                time.sleep(5)






