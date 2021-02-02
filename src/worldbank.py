import csv
import logging
from src.common import make_req, get_country_codes, filter_by_key, generate_file_address, write_to_csv, call_conan
from src.models.input import WorldbankInput as Input


def _get_for_period(data, start, end):
    return [x for x in data
            if x["date"] != None
            and int(x["date"]) >= start
            and int(x["date"]) <= end]


def _convert_to_iso3(data):
    def convert_iso3_datum_to_ison(datum):
        return {
            **datum,
            "country": call_conan(datum["countryiso3code"]),
        }

    data_isonum = list(map(convert_iso3_datum_to_ison,
                           data))
    data_isonum = [x for x in data_isonum if x["country"] != None]
    return data_isonum


def _handle_single_country(data, country_code):
    # for each country, get list of values from data
    country_data = [
        x for x in data if x["country"] == country_code]

    # return None if no value available
    if(len(country_data) <= 0):
        return

    # sort to set latest values first
    country_data_sorted = sorted(
        country_data, key=lambda k: int(k['date']), reverse=True)

    # get latest value for country, don't get date
    latest = country_data_sorted[0]
    latest = {
        "country": latest["country"],
        "value": latest["value"]
    }
    return latest


def _handle_single_worldbank(code, start, end):

    print(f"getting data for {code['code']}({code['name']})...")

    print(code["url"])

    # fetch all
    res = make_req("GET", code["url"])
    data = res[1]  # the second list item are list of data

    # get past N years
    data_recent = _get_for_period(data, start, end)

    # get non null
    data_nonnull = [x for x in data_recent if x["value"] != None]

    # get keys we care about
    data_filtered_by_key = filter_by_key(
        data_nonnull, ["countryiso3code", "value", "date"])

    # convert country codes to isonumeric
    data_isonum = _convert_to_iso3(data_filtered_by_key)

    # get countries we look for
    country_codes = get_country_codes()

    data_latest = []

    for country in country_codes:
        latest_country_value = _handle_single_country(
            data_isonum, int(country))
        if(latest_country_value != None):
            data_latest.append(latest_country_value)

    # write to csv
    file_address = generate_file_address(code["code"])

    write_to_csv(data=data_latest,
                 keys=data_latest[0].keys(), file_address=file_address)


def handle_worldbank(**period):
    """Collects latest available datapoints given a start and end year for Worldbank codes defined in /data

    Parameters
    -------
    start: `int` 
        The starting year to get the data for

    end: `int`
        The last year to get the data for
    """
    period = Input(**period)

    with open('data/codes/worldbank_codes.csv') as codes_file:
        codes = csv.DictReader(codes_file, delimiter=',', quotechar='"')
        codes = list(codes)[:2]
        for code in codes:
            _handle_single_worldbank(
                code=code, start=period.start, end=period.end)
