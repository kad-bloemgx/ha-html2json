import requests
from bs4 import BeautifulSoup
from datetime import datetime
import json
import os
import argparse
import re

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

    latest_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    for row in rows[1:]:
        columns = row.find_all('td')
        if len(columns) == 6:
            base_id = columns[0].text.strip()
            power_data[base_id] = [clean_value(columns[1].text, {'W': ''}),
                                   clean_value(columns[2].text, {'Hz': ''}),
                                   clean_value(columns[3].text, {'V': '', 'A:':'', 'B:':'', 'C:':''}),
                                   clean_value(columns[4].text, {'°C': ''}, is_temperature=True),
                                   columns[5].text.strip() if columns[5].text.strip() else latest_time]

    return power_data

def save_power_data(power_data):
    with open('./www/power_data_inverter.json', 'w') as outfile:
        json.dump(power_data, outfile, indent=4)


def main():
    parser = argparse.ArgumentParser(description='Process and collect solar data.')
    parser.add_argument('--file', type=str, help='Path to local HTML file')
    parser.add_argument('--url', type=str, help='URL to fetch the HTML content')

    args = parser.parse_args()

    html_content = get_html_content(args.file, args.url)
    if html_content:
        power_data = parse_table(html_content)
        if power_data:
            save_power_data(power_data)

if __name__ == "__main__":
    main()
