import json
import os
from pathlib import Path

from jinja2 import Environment, FileSystemLoader, select_autoescape
from livereload import Server
from more_itertools import chunked


def on_reload():
    env = Environment(
        loader = FileSystemLoader('.'),
        autoescape = select_autoescape(['html', 'xml']))

    template = env.get_template('template.html')

    Path('pages').mkdir(parents = True,
                        exist_ok = True)

    with open("books_params.json", "r", encoding="utf-8") as my_file:
        books_params = json.load(my_file)

    quantity_books_in_page = 10
    books_params = list(chunked(books_params, quantity_books_in_page))

    for number, book_params in enumerate(books_params, start = 1):
        quantity_books_in_raw = 2
        book_params = list(chunked(book_params, quantity_books_in_raw))
        rendered_page = template.render(
            books_params = book_params,
            page_number = number,
            pages = len(books_params))
        with open(os.path.join('pages', f'index{number}.html'),
                  'w', encoding="utf8") as file:
            file.write(rendered_page)


if __name__ == '__main__':
    on_reload()

    server = Server()
    server.watch('template.html', on_reload)
    server.watch('books_params.json', on_reload)
    server.serve(root = '.')

