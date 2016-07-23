#!/usr/bin/env python
#-*- coding: utf-8 -*-

from bs4 import BeautifulSoup as BS
from subprocess import call as s_call
from requests import get as re_get
from os import mkdir, listdir
from os.path import join, exists

BOOK_DIR    = "out"
BOOK_NAME   = "[{0}]-{1}.html"
ROOT_URL    = "http://www.imperial-library.info"

# Really crappy check to see if we have a local bin or not 
KGEN_BIN    = "kindlegen" if "kindlegen" not in listdir(".") else "./kindlegen"

SOURCE_URLS = {
    "daggerfall"  : "/books/daggerfall/by-title",
    "battlespire" : "/books/battlespire/by-title",
    "redguard"    : "/books/redguard/by-title",
    "morrowind"   : "/books/morrowind/by-title",
    "shadowkey"   : "/books/shadowkey/by-title",
    "oblivion"    : "/books/oblivion/by-title",
    "skyrim"      : "/books/skyrim/by-title",
    "online"      : "/books/online/by-title",
    }

# We have to re-write an OPF file with each book's details 
OPF_BLOB    = """
<?xml version="1.0" encoding="iso-8859-1"?>
<package unique-identifier="uid" xmlns:opf="http://www.idpf.org/2007/opf" xmlns:asd="http://www.idpf.org/asdfaf">
    <metadata>
        <dc-metadata  xmlns:dc="http://purl.org/metadata/dublin_core" xmlns:oebpackage="http://openebook.org/namespaces/oeb-package/1.0/">
            <dc:Title>{0}</dc:Title>
            <dc:Language>en</dc:Language>
            <dc:Creator>{1}</dc:Creator>
            <dc:Copyrights>Bethesda</dc:Copyrights>
            <dc:Publisher>Bethesda</dc:Publisher>
        </dc-metadata>
    </metadata>
    <manifest>
        <item id="text" media-type="text/x-oeb1-document" href="index.html"></item>
    </manifest>
    <spine toc="ncx">
        <itemref idref="text"/>
    </spine>
    <guide>
        <reference type="text" title="Book" href="index.html"/>
    </guide>
</package>
"""

HTML_BLOB = """
<html>
<head><style>.rtecenter{text-align:center;}</style></head>
<body>
{0}
</body>
</html>
"""

def craft_url(url):
    return "{}{}".format(ROOT_URL, url)

def get_bs(url):
    return BS(re_get(craft_url(url)).text, 'html.parser')

def craft_fname(section, url):
    return BOOK_NAME.format(section, url.split("/").pop())

def isnt_empty(tag):
    if tag.text.strip() == "\xa0" or tag.text.replace("\xa0", " ").strip() == "":
        return False
    return True

def run_kindlegen(section, url):
    return call(["kindlegen", "-o", "something.mobi", "data.html"])

def gather_text(bs):
    node_root = bs.find_all("div", class_="node-content")
    paras = [x for x in node_root[1].find_all("p")]
    return paras

def main(*args, **kwargs):
    book_hrefs = list() # list to collect all HREFs gathered

    # first check whether we have an output directory
    if not exists(BOOK_DIR):
        print("Creating book output directory")
        mkdir(BOOK_DIR)
        print("Creating sub-directories")
        for game in SOURCE_URLS.keys():
            mkdir(join(BOOK_DIR, game))
        print("Done")

    for game, source_url in SOURCE_URLS.items():
        print("Running downloads on {}...".format(source_url))
        index = get_bs(source_url) # get the BS of the current index
        book_hrefs.extend([(game, x['href']) for x in index.find_all("div", class_="view-content")[0].find_all("a")])
    print("Total count: {}".format(len(book_hrefs)))

    # Download each book page's data, check if it contains multiple books
    # Export the data to an HTML/OPF file, render each one one-by-one to 
    # it's respective folder
    for game, href in book_hrefs:
        raw_bs = get_bs(href)
        vol_ls = raw_bs.find_all("div", class_="book-navigation")
        if vol_ls:
            s_href = [x.a["href"] for x in vol_ls[0].find_all('li')]
            s_bses = [get_bs(href) for href in s_href]
        else:
            s_href = [href]
            s_bses = [raw_bs]

        for url, bs in zip(s_href, s_bses):
            with open("output.html", "w") as hf:
                f.write("test")

            with open("book.opf", "w") as of:
                f.write("test")

    return None

if __name__ == "__main__":
    main()

# end

