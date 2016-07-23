#!/usr/bin/env python
#-*- coding: utf-8 -*-

from bs4 import BeautifulSoup as BS   # parser
from subprocess import call as s_call # sub-system call
from requests import get as re_get    # fetch data from URI
from os import mkdir, listdir         # list and make directories
from os.path import join, exists      # check path exists, join path strings
from shutil import move as fmove      # file moving
from string import printable as printable_chrs # printable characters
from sys import argv                  # obvious

# Output settings
OUTDIR      = "out"
OUTNAME     = "{1}.mobi"
ROOT_URL    = "http://www.imperial-library.info"

# Really crappy check to see if we have a local bin or not 
KGEN_BIN    = "kindlegen" if "kindlegen" not in listdir(".") else "./kindlegen"

# All games organized by section
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
# Kindlegen uses the OPF XML file as a way of writing info about the book
# No point in creating a complex ETree to express this when I'm changing two things
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
        <item id="text" media-type="text/x-oeb1-document" href="output.html"></item>
    </manifest>
    <spine toc="ncx">
        <itemref idref="text"/>
    </spine>
    <guide>
        <reference type="text" title="Book" href="output.html"/>
    </guide>
</package>
"""

# The HTML of the book, doesn't have to be very complex
HTML_BLOB = """
<html>
<head><style>.rtecenter{{text-align:center;}}</style></head>
<body>
{0}
</body>
</html>
"""

def craft_url(url):
    """
    Return a URL using the ROOT_RUL variable at top-level
    """
    return "{}{}".format(ROOT_URL, url)

def get_bs(url):
    """
    Return a parser of the given URL fragment
    /content/something-id -> BS(ROOT_URL/content/something-id)
    Applies a ton of filtering/replacing so we don't get bad characters
    """
    text = re_get(craft_url(url)).text
    text = "".join([c for c in text if c in printable_chrs])
    text = text.replace("\n", " ").replace("\xa0", " ")
    return BS(text, 'html.parser')

def craft_fname(section, url):
    """
    Craft a filename for moving the MOBI file
    """
    return OUTNAME.format(section, url.split("/").pop())

def run_kindlegen():
    """
    Call the kindlegen compiler to create an output MOBI blob
    The blob then has to be moved by the program to a folder
    """
    return s_call([KGEN_BIN, "-o", "output.mobi", "book.opf"])

def get_title(bs, game):
    """
    Return the title of the given book BS
    Luckily it seems to be the only H1 tag in the BS
    """
    return "[{0}] {1}".format(game.capitalize(), bs.h1.text)

def get_author(bs):
    """
    Find the author name, which exists in a strange div next to some strange 
    characters, next to a text label of "Author", so we must remove 
    all of that to extract the final Author name
    """
    auth = bs.find_all("div", class_="field-item odd")
    if not len(auth):
        return ""
    auth = auth[0].text.replace("Author:", "")
    auth = "".join([c for c in auth if c in printable_chrs]).strip()
    return auth

def gather_text(bs):
    """
    Collect all paragraphs under the node-content div
    These can be joined later but for now, only return a list
    '\xa0' gets inserted by BS so we have to clear it after it parses
    """
    node_root = bs.find_all("div", class_="node-content")
    return [str(p).replace("\xa0", " ") for p in node_root[1].find_all("p")]

def to_book(game, url):
    """
    Main book algorithm
    1. first detect if a given URL is a listing of multiple books
    2. then pass the URL(s) to a processing section where we write files
    3. Run kindlegen on the newly created html/opf blobs
    4. Move the MOBI output into it's respective folder with it's new name
    """
    raw_bs = get_bs(url)
    vol_ls = raw_bs.find_all("div", class_="book-navigation")

    if vol_ls: # this page contains listing for multiple books
        s_href = [x.a["href"] for x in vol_ls[0].find_all("li")]
        s_bses = [get_bs(href) for href in s_href]
    else:      # this page is the only book
        s_href = [url]
        s_bses = [raw_bs]

    # Write HTML, OPF, and run the compiler
    for url, bs in zip(s_href, s_bses):
        with open("output.html", "w") as hf:
                hf.write(HTML_BLOB.format("\n".join(gather_text(bs))))

        with open("book.opf", "w") as of:
            of.write(OPF_BLOB.format(get_title(bs, game), get_author(bs)))

        try:
            run_kindlegen() # run the compiler
            fmove("output.mobi", join(OUTDIR, game, craft_fname(game, url)))
        except Exception as e:
            print("Error occurred: {}".format(str(e)))
    return True 

def main(*args, **kwargs):
    """
    Main program to set up the processing
    """
    book_hrefs = list() # list to collect all HREFs gathered

    # first check whether we have an output directory
    if not exists(OUTDIR):
        print("Creating book output directory")
        mkdir(OUTDIR)
        print("Creating sub-directories")
        for game in SOURCE_URLS.keys():
            mkdir(join(OUTDIR, game))
        print("Done creating directories")

    # Build a list of URLs to scan from each index
    for game, source_url in SOURCE_URLS.items():
        print("Downloading index of {}...".format(source_url))
        index = get_bs(source_url) # get the BS of the current index
        book_hrefs.extend([(game, x['href']) for x in index.find_all("div", class_="view-content")[0].find_all("a")])
    print("Total count: {}".format(len(book_hrefs)))

    # Process each URL and it's game to the to_book() function
    count = 0
    for game, href in book_hrefs:
        print("Processing {}...".format(href))
        to_book(game, href)
        count += 1
        print("{0} books processed".format(count))

    # end
    return None


if __name__ == "__main__":
    if "-t" in argv or "--test" in argv:
        print("Testing")
        quit()
    main()

# end

