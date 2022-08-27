import argparse

import requests
from bs4 import BeautifulSoup


def check_for_redirect(response):
    if response.history:
        raise requests.TooManyRedirects


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
    for number in range(start_id, end_id + 1):
        text_url = 'https://tululu.org/txt.php'
        payload = {'id': number}
        text_response = requests.get(text_url, params=payload)
        try:
            check_for_redirect(text_response)

            title_url = f'https://tululu.org/b{number}/'
            title_response = requests.get(title_url)

            parse_book_page(response=title_response,
                            number=number)
        except requests.TooManyRedirects:
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

    parse_tululu(start_id=args.start_id,
                 end_id=args.end_id)
