



import requests
import json
import os
from bs4 import BeautifulSoup
from datetime import datetime

data_file = 'price_data.json'

def get_item_info(url):
    response = requests.get(url)
    response.status_code
    soup = BeautifulSoup(response.content, 'html.parser')
    price_text = soup.find('span', class_='price-primary', itemprop='price').get_text(strip=True)

    data = {'name':     soup.find('h1', id='productName').get_text(strip=True),
            'price':    float(price_text.replace('$', '').replace(',', '')),
            }
    return data

def read_in_price_data():
    with open(data_file, "r") as file:
        return json.load(file)

def write_price_data(output_data):
    with open(data_file, "w") as file:
        json.dump(output_data, file, indent=4)


if __name__ == '__main__':
    item_list = [
        'https://www.cabelas.ca/product/4881/ruger-1022-22lr-rotary-magazine',
        'https://www.cabelas.ca/product/87847/tikka-t3x-lite-stainless-bolt-action-rifle',
        'https://www.cabelas.ca/product/4883/ruger-1022-stainless-synthetic-semi-auto-rifle',
    ]

    # Get the current date and format the date as YYYY-MM-DD
    current_date = datetime.now()
    formatted_date = current_date.strftime("%Y-%m-%d")

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
            if stored_data[url]['price_history'][0][1] == queried_data[url]['price']:
                print('Price did not change')
                stored_data[url]['price_history'][0] = [formatted_date, queried_data[url]['price']]
        else:
            stored_data[url]['price_history'].insert(0, [formatted_date, queried_data[url]['price']])
    write_price_data(stored_data)


# import requests
# from bs4 import BeautifulSoup
#
#
# def get_item_price(url):
#     # Send a GET request to the item URL
#     response = requests.get(url)
#
#     # Check if the request was successful
#     if response.status_code == 200:
#         # Parse the HTML content with BeautifulSoup
#         soup = BeautifulSoup(response.content, 'html.parser')
#
#         # Find the price element (Cabela's price usually has a specific class or ID)
#         price_element = soup.find('span', {'class': 'price-primary'})  # You may need to inspect the HTML
#         if price_element:
#             # Extract the text and clean it up
#             price_text = price_element.get_text(strip=True)
#             price = float(price_text.replace('$', '').replace(',', ''))  # Convert to a float
#             return price
#         else:
#             print("Price element not found.")
#             return None
#     else:
#         print(f"Failed to retrieve the page: {response.status_code}")
#         return None
#
#
# # Press the green button in the gutter to run the script.
# if __name__ == '__main__':
#     get_item_price('https://www.cabelas.ca/product/4883/ruger-1022-stainless-synthetic-semi-auto-rifle')
#     # print_hi('PyCharm')
#
# # See PyCharm help at https://www.jetbrains.com/help/pycharm/
