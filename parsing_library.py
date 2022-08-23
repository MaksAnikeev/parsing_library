import requests
from pathlib import Path

Path('books').mkdir(parents=True, exist_ok = True)

for i in range(10):
    url = f'https://tululu.org/txt.php?id={i+1}'
    response = requests.get(url)
    response.raise_for_status()
    with open(f'books/book_{i+1}.txt', 'w', encoding='UTF-8') as file:
        file.write(response.text)



