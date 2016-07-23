#!/usr/bin/env python
#-*- coding: utf-8 -*-

from bs4 import BeautifulSoup
from requests import get as re_get
from xml import etree as ET

base_url = "http://www.imperial-library.info"
maid_url = "/content/lusty-argonian-maid"

def get_bs(url):
    return BeautifulSoup(re_get("{}{}".format(base_url, url)).text, 'html.parser')

bs = get_bs(maid_url)

# polishing spear begins below

# Determine whether there are multiple books (if this page is a collection)
# Collections have a list div but they are numbered differently per coll
# Else, we treat the given BS as a normal book item

volumes_listing = bs.find_all("div", class_="book-navigation")

search_items = list()
if volumes_listing:
    search_hrefs = [x.a["href"] for x in volumes_listing[0].find_all('li')]
    search_items = [get_bs(href) for href in search_hrefs]
else:
    search_hrefs = [maid_url]
    search_items = [bs]

# Gather all the paragraphs of a given bs item
def gather_text(bs):
    node_root = bs.find_all("div", class_="node-content")
    paras = [x for x in node_root[1].find_all("p")]
    return paras

def craft_fname(uri):
    """
    Turn a /path/to/text string into a text.html string
    """
    return "{}.html".format(uri.split("/").pop())

def isnt_empty(tag):
    if tag.text.strip() == "\xa0" or tag.text.replace("\xa0", " ").strip() == "":
        return False
    return True

for uri, bs in zip(search_hrefs, search_items):
    with open(craft_fname(uri), "w") as f:
        f.write("<html>")
        f.write("<head>")
        f.write("<title>{}</title>".format("x d"))
        f.write("<meta charset='utf-8'>")
        f.write("</head><body>\n")
        for para in filter(isnt_empty, gather_text(bs)):
            f.write("{}\n".format(str(para)))
        f.write("</body></html>")

print("Done")

