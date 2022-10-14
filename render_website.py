from http.server import HTTPServer, SimpleHTTPRequestHandler
import json
import os

from jinja2 import Environment, FileSystemLoader, select_autoescape
from livereload import Server
from more_itertools import chunked

def on_reload(folder):
    env = Environment(
        loader=FileSystemLoader('.'),
        autoescape=select_autoescape(['html', 'xml'])
    )

    template = env.get_template('template.html')

    with open("books_params.json", "r", encoding="utf-8") as my_file:
        books = my_file.read()
        books_params = json.loads(books)

    books_params = list(chunked(books_params, 10))

    for number, book_params in enumerate(books_params):
        book_params = list(chunked(book_params, 2))
        rendered_page = template.render(
            books_params=book_params,
        )
        with open(os.path.join(folder, f'index {number+1}.html'), 'w', encoding="utf8") as file:
            file.write(rendered_page)


os.makedirs('pages', mode=0o777, exist_ok=False)
on_reload(folder='pages')


server = Server()
server.watch('template.html', on_reload)
server.watch('books_params.json', on_reload)
server.serve(root='.')