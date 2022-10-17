import json
import os
from pathlib import Path

from jinja2 import Environment, FileSystemLoader, select_autoescape
from livereload import Server
from more_itertools import chunked


def on_reload():
    env = Environment(
        loader=FileSystemLoader('.'),
        autoescape=select_autoescape(['html', 'xml'])
    )

    template = env.get_template('template.html')

    Path('pages').mkdir(parents=True,
                        exist_ok=True)

    with open("books_params.json", "r", encoding="utf-8") as my_file:
        books = my_file.read()
        books_params = json.loads(books)

    books_params = list(chunked(books_params, 10))

    for number, book_params in enumerate(books_params):
        book_params = list(chunked(book_params, 2))
        rendered_page = template.render(
            books_params=book_params,
            page_number=number + 1,
            pages=len(books_params)
        )
        with open(os.path.join('pages', f'index{number + 1}.html'), 'w', encoding="utf8") as file:
            file.write(rendered_page)


on_reload()

server = Server()
server.watch('template.html', on_reload)
server.watch('books_params.json', on_reload)
server.serve(root='.')

