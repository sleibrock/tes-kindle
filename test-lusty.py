#!/usr/bin/env python
#-*- coding: utf-8 -*-

from bs4 import BeautifulSoup
from requests import get as re_get
from xml.etree import ElementTree

maid_url = "http://www.imperial-library.info/content/lusty-argonian-maid"

def get_bs(url):
    return BeautifulSoup(re_get(url).text, 'html.parser')

bs = get_bs(maid_url)


# polishing spear begins below

# Determine whether there are multiple books (if this page is a collection)
# Collections have a list div but they are numbered differently per coll
# Else, we treat the given BS as a normal book item

volumes_listing = bs.find_all("div", class_="book-navigation")

if volumes_listing:
    print("There's volumes!")
else:
    print("There isn't")


