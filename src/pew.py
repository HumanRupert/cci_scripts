import logging
import warnings

import pandas as pd

from src.common import get_country_codes, generate_file_address, write_to_csv, call_conan


def handle_pew_rdi(path):
    """Given the URL of the most recent Religious Diversity Index's Excel file, collects RDI data 

    Parameters
    ----------
    path : `str`
        Remote or local path to the Excel file
    """
    # read excel
    rdi = pd.read_excel(path, usecols=["Country", "RDI"])

    # convert country codes to ISO3
    rdi["Country"] = rdi["Country"].apply(lambda country: call_conan(country))

    # remove null
    rdi = rdi.dropna()

    # get available country codes
    available_country_codes = get_country_codes()
    available_country_codes = [int(cc) for cc in available_country_codes]

    # get available country codes values from RDI
    rdi = rdi[rdi["Country"].isin(available_country_codes)]

    # rename RDI col to value, to standardize w/ other output files
    rdi = rdi.rename(columns={'RDI': 'value'})

    # change headers to lowercase
    rdi.columns = map(str.lower, rdi.columns)

    # write to csv
    code = pd.read_csv("data/codes/pew_codes.csv").iloc[0]["code"]
    file_address = generate_file_address(code)
    keys = rdi.columns
    data = rdi.to_dict("records")
    write_to_csv(data=data, keys=keys, file_address=file_address)
