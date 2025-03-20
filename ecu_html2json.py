from typing import TextIO

import requests
from bs4 import BeautifulSoup
import json
import os
import argparse
import re
from pathlib import Path
""" 
1. get_html_content     # scrape table from ECU
2. parse_table          # parse table to JSON document
3. clean_value          # filter van de data
4. save_power_data      # save JSON document to file
"""

def clean_value(value, replace_dict, is_temperature=False):
    for key, replacement in replace_dict.items():
        value = value.replace(key, replacement)
    cleaned_value = value.strip()
    if is_temperature:
        cleaned_value = re.sub(r'[^\d.]+', '', cleaned_value)  # Remove everything except digits and dot
    return '0' if cleaned_value in ['', '-', '�'] else cleaned_value

def get_html_content(file_path, url):
    if file_path and os.path.exists(file_path):
        with open(file_path, 'r') as f:
            html_content = f.read()
    else:
        r = requests.get(url)
        if r.status_code != 200:
            print('Error:', r.status_code)
            return None
        html_content = r.text
    return html_content

def parse_table(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    table = soup.find('table')

    if table is None:
        print('No table found')
        return None

    rows = table.find_all('tr')
    power_data = {}

    for row in rows[0:]:
        columns = row.find_all('td')
        if len(columns) == 2:
            omschrijving = columns[0].text.strip()
            power_data[omschrijving] = [clean_value(columns[1].text, {'kWh': '', 'W':'', 'kB': ''})]

    return power_data

def exist_file_power_data(file):

    filename = Path(file)

    if filename.exists():
        return True
    else:
        return False

def value_generation_of_current_day_greater_or_equal(power_data, file):
    """Controleer of de opgeslagen waarde groter of gelijk is aan de waarde in de ECU"""

    x = power_data.get("Generation Of Current Day")
    #print(x)

    if exist_file_power_data(file):

        with open(file) as json_data:
            d = json.load(json_data)

        y = d['Generation Of Current Day']
        #print(y)

        if x >= y:
            return True
        else:
            return False

    else:

        return True

def print_power_data(power_data):

    """print("Keys and Values:")
    for key, value in power_data.items():
            print(f"{key}: {value}") """

    x = power_data.get("Generation Of Current Day")
    print(x)


    with open(power_data) as json_data:
        d = json.load(json_data)
        #print(d)
        y = d['Generation Of Current Day']
        print(y)

    if x >= y:
        print("valid")
    else:
        print("invalid")

def save_power_data(power_data) -> None:

    with open('./www/power_data_ecu.json', 'w+') as outfile:
        json.dump(power_data, outfile, indent=4)

    with open('./www/power_data_ecu1.json', 'w+') as outfile:
        json.dump(power_data.get('ECU ID'), outfile, indent=4)

def main():
    parser = argparse.ArgumentParser(description='Process and collect solar data.')
    parser.add_argument('--file', type=str, help='Path to local HTML file')
    parser.add_argument('--url', type=str, help='URL to fetch the HTML content')

    args = parser.parse_args()

    html_content = get_html_content(args.file, args.url)
    if html_content:
        power_data = parse_table(html_content)
        if power_data:
            # if value_generation_of_current_day_greater_or_equal(power_data, './www/power_data_ecu.json'):

                save_power_data(power_data)

            #else:
                #print("fout")
                #exit()


if __name__ == "__main__":
    main()
