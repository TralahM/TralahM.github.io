#!/usr/bin/env python

from bs4 import BeautifulSoup as BS
import requests
import pandas as pd
import csv
import argparse


url = "https://www.xoserve.com/help-centre/demand-attribution/unidentified-gas-uig/chart-uig-by-gas-day/"
base_url = "https://www.xoserve.com"


def scrape_and_save_to(output_file):
    response = requests.get(url)
    content = response.content
    soup = BS(content, "lxml")
    list_docs = soup.find("div", {"class": "list-documents"})
    if list_docs is None:
        return
    a_link = list_docs.find("a", {"target": "_blank"})
    if a_link is None:
        return
    link = a_link.attrs.get("href")
    if link is None:
        return
    file_link = base_url + link
    # print(file_link)
    df = pd.read_excel(
        file_link,
        names=[
            "GasDay",
            "D_plus_1_pct",
            "D_plus_5_pct",
        ],
    )
    # df.head()
    df.to_csv(
        output_file,
        encoding="utf-8",
        lineterminator="\n",
        quotechar='"',
        quoting=csv.QUOTE_ALL,
        index=False,
    )
    print(f"Saved csv to {output_file}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("filename", help="output filename")
    args = parser.parse_args()
    output_file = args.filename
    scrape_and_save_to(output_file)


if __name__ == "__main__":
    main()
