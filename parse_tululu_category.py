import requests
from bs4 import BeautifulSoup
import re


def parse_category_page(response):
    soup = BeautifulSoup(response.text, 'lxml')
    books_id = []
    books = soup.find_all(class_='d_book')
    for book in books:
        book_str_id = book.find('a')['href']
        book_id = int(re.findall(r'-?\d+\.?\d*', book_str_id)[0])
        books_id.append(book_id)

    return books_id


if __name__ == '__main__':
    for number in range(3):
        category_url = f'https://tululu.org/l55/{number}/'
        category_response = requests.get(category_url)
        category_response.raise_for_status()
        books_range = parse_category_page(category_response)
        for number in books_range:
            book_url = f'https://tululu.org/b{int(number)}/'
            print(book_url)
