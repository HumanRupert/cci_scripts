import requests
import logging
import csv
import time
import warnings

import country_converter as coco


def make_req(method, url, params={}, headers={}):
    # https://stackoverflow.com/a/38489588/10295948
    headers["User-Agent"] = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36"

    try:
        response = requests.request(
            method, url, data=params, headers=headers)
        response.raise_for_status()
    except requests.RequestException as e:
        logging.error(response.json())
        raise

    return response.json()


def filter_by_key(data, keys):
    return [
        {key: x[key] for key in keys}
        for x in data
    ]


def get_country_codes():
    country_codes_file = open('data/iso_numbers.csv')
    country_codes = csv.reader(
        country_codes_file, delimiter=',', quotechar='"')
    country_codes = list(country_codes)

    # flatten the results, remove the first element (table title)
    country_codes = [
        item for sublist in country_codes for item in sublist][1:]

    country_codes_file.close()

    return country_codes


def generate_file_address(code):
    millis = time.time() * 1000
    filename = f"{code}–{millis}.csv"
    fileaddress = f"out/{filename}"
    return fileaddress


def write_to_csv(data, keys, file_address):
    with open(file_address, 'w') as file:
        writer = csv.DictWriter(file, keys)
        writer.writeheader()
        writer.writerows(data)


def call_conan(country, to="isocode"):
    coco_logger = coco.logging.getLogger()
    coco_logger.setLevel(logging.CRITICAL)

    # https://stackoverflow.com/a/57986495/10295948
    warnings.filterwarnings("ignore")

    return coco.convert(country, to=to, not_found=None)
