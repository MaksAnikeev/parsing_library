from http.server import HTTPServer, SimpleHTTPRequestHandler
import json

from jinja2 import Environment, FileSystemLoader, select_autoescape
from livereload import Server
from more_itertools import chunked

def on_reload():
    env = Environment(
        loader=FileSystemLoader('.'),
        autoescape=select_autoescape(['html', 'xml'])
    )

    template = env.get_template('template.html')

    with open("books_params.json", "r", encoding="utf-8") as my_file:
        books = my_file.read()
        books_params = json.loads(books)

    books_params = list(chunked(books_params, 2))
    rendered_page = template.render(
        books_params=books_params,
    )

    with open('index.html', 'w', encoding="utf8") as file:
        file.write(rendered_page)

on_reload()

server = Server()
server.watch('template.html', on_reload)
server.watch('books_params.json', on_reload)
server.serve(root='.')