#!/usr/bin/env python
from selenium import webdriver
from argparse import ArgumentParser

browser = webdriver.Firefox(executable_path="/usr/local/bin/geckodriver")

if __name__ == "__main__":
    psr = ArgumentParser()
    psr.add_argument("-f", action="store", dest="name")
    arg = psr.parse_args().name
    browser.get(arg)
