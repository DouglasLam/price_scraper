import requests
import os
from bs4 import BeautifulSoup
from datetime import datetime
from tabulate import tabulate

from flask import Flask, render_template, jsonify
import json
import copy

data_file = 'price_data.json'

app = Flask(__name__)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/data")
def get_data():
    process_item_list_and_update_json()
    with open("price_data.json") as f:
        data = json.load(f)
    return jsonify(data)

def get_item_info(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    price_text = soup.find('span', class_='price-primary', itemprop='price').get_text(strip=True)
    image_url = soup.find('img', class_='product-main-image')['src']

    data = {
        'name': soup.find('h1', id='productName').get_text(strip=True),
        'price': float(price_text.replace('$', '').replace(',', '')),
        'image_url': image_url
    }
    return data


def read_in_price_data():
    with open(data_file, "r") as file:
        lines = [line.strip() for line in file.readlines()]
        if not lines:
            print(f"The file {data_file} is empty.")
            return {}
        file.seek(0)  # Reset file pointer to the beginning
        return json.load(file)


def write_price_data(output_data):
    with open(data_file, "w") as file:
        json.dump(output_data, file, indent=4)


def output_prices_to_table(stored_data):
    headers = ["Item", "Price", "Latest Date", "Previous Price", "Previous Date"]

    data = []
    for key, value in stored_data.items():
        name = value['name']
        price = value['price_history'][0]['date']
        date = value['price_history'][0]['price']
        previous_price = "N/A"
        previous_date = "N/A"
        if len(value['price_history']) > 1:
            previous_price = value['price_history'][1]['price']
            previous_date = value['price_history'][1]['date']
        data.append([name, price, date, previous_price, previous_date])

    print(tabulate(data, headers=headers, tablefmt="grid"))


def read_urls_from_file(file_path):
    with open(file_path, "r") as file:
        return [line.strip() for line in file.readlines()]


def process_item_list_and_update_json():
    url_file = "urls.txt"
    item_list = read_urls_from_file(url_file)

    current_date = datetime.now()
    formatted_date = current_date.strftime("%Y-%m-%d %I:%M:%S %p")

    stored_data = {}
    queried_data = {}
    if os.path.isfile(data_file):
        stored_data = read_in_price_data()

    for url in item_list:
        queried_data[url] = get_item_info(url)
        if url not in stored_data.keys():
            stored_data[url] = {}
        if 'price_history' not in stored_data[url]:
            stored_data[url]['price_history'] = []
            stored_data[url]['name'] = queried_data[url]['name']
        if len(stored_data[url]['price_history']) > 0:
            if stored_data[url]['price_history'][0]['price'] == queried_data[url]['price']:
                print('Price did not change')
                stored_data[url]['price_history'][0] = {'date': formatted_date, 'price': queried_data[url]['price']}
        else:
            stored_data[url]['price_history'].insert(0, {'date': formatted_date, 'price': queried_data[url]['price']})
        stored_data[url]['image_url'] = queried_data[url]['image_url']
    write_price_data(stored_data)
    output_prices_to_table(stored_data)


if __name__ == '__main__':
    process_item_list_and_update_json()
    app.run(debug=True)

