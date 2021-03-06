#!/usr/bin/env python3
"""Take a bunch of links, probably generated by water_skimmer, and look for interesting ones."""

import os
import time
import multiprocessing
import urllib.request
from urllib.error import URLError, HTTPError
from ssl import SSLError
from socket import timeout
from http.client import RemoteDisconnected
from tldextract import extract


CSVFILE = "top-1m.csv" # CSV file containing alexa top 1 million websites ranking
NUM_RANKS = 1000000    # Number of ranks, so we can say "this website is more than the 1mil rank!"

# Directory files are stored in, where each file in the directory contains
# links to analyze separated by newlines.
LINKDIR = "links"

# How many interesting links to find
NUM_INTERESTING = 100

DEBUG = True

# Load ranks into memory
WS_RANKS = {}
with open(CSVFILE, 'r') as f:
    for line in f:
        v, k = tuple(map(lambda x: x.strip(), line.split(',')))
        WS_RANKS[k] = int(v)


def resolve_url(url):
    """Take a URL, and find out where it goes. Follow redirects for URL aliases, shortlinks, etc.
       Very slow."""
    start = time.time()
    # Return something with a rank of 1, so we get alerted that the URL is not interesting
    return_if_bad_url = "http://www.google.com"
    # Protocol must be specified.
    if not url.startswith("http"):
        url = "http://"+url
    if url.endswith('.'):
        url = url[:-1]

    try:
        req = urllib.request.Request(url)
        res = urllib.request.urlopen(req, timeout=10)
        # print(multiprocessing.current_process().name.split('-')[1]+ ' ' + str(time.time()-start))
        return res.geturl()
    except HTTPError as err:
        # Some finer-grained handling might be nice
        # Sometimes fails on a 403 where it doesn't need to. (eg. http://dot.net)
        # print(multiprocessing.current_process().name.split('-')[1]+ ' ' + str(time.time()-start))
        return return_if_bad_url

    # Unrecoverables.
    except (URLError, SSLError, timeout, RemoteDisconnected, TypeError, UnicodeError, ConnectionResetError) as err:
        # print(multiprocessing.current_process().name.split('-')[1]+ ' ' + str(time.time()-start))
        return return_if_bad_url


def baseurl(url):
    """Get the domain and suffix of a URL.
    example: baseurl('https://wwww.subdir.website.co.uk/pages/one.php') -> website.co.uk"""
    temp = extract(url)
    return temp.domain + '.' + temp.suffix

def get_rank(wsname):
    """Take a website name and find its rank in the alexa top 1 million"""
    try:
        return WS_RANKS[baseurl(wsname)]
    except KeyError:
        return NUM_RANKS + 1

def resolve_rank(wsname):
    """Resolve a URL, and find the rank of the returned URL."""
    try:
        return WS_RANKS[baseurl(resolve_url(baseurl(wsname)))]
    except KeyError:
        return NUM_RANKS + 1

def sort_rank(wslist):
    """Sort a list of URLs by the popularity of their domains, descending."""
    return sorted(wslist, key=get_rank)

def sort_resolve(wslist):
    """Sort a list of URLs by the popularity of the domains of the URLs' destinations."""
    rankeddict = {}
    pool = multiprocessing.Pool(processes=4, maxtasksperchild=2)
    pool_resolved_ranks = pool.map(resolve_rank, wslist)
    # print(pool_resolved_ranks)
    pool.close()

    # Remove websites we thought were interesting, but aren't.
    for index, siteurl in enumerate(wslist):
        rank_resolved = pool_resolved_ranks[index]
        rank_unresolved = get_rank(siteurl)
        # If we find the one that's an error, drop it
        # If we find one that resolved to a more common site, drop it.
        # Implementation detail: google.com is always dropped.
        if rank_resolved != 1 and rank_resolved >= rank_unresolved:
            rankeddict[siteurl] = rank_resolved
            # print(str(rank_resolved) + " " + siteurl)

    return sorted(rankeddict, key=rankeddict.__getitem__)


def getlinks():
    """Slurp the contents of the linkfiles into one big list.
    Each linkfile contains URLs separated by newlines and is located in LINKDIR."""
    collected_links = []
    for filename in os.listdir(LINKDIR):
        with open(os.path.join(LINKDIR, filename), 'r') as linkfile:
            collected_links.extend([line.strip() for line in linkfile.readlines()])
    return collected_links

def mostinteresting(linklist):
    """Take a list of links and return *up to* NUM_INTERESTING links, ranked by interestingness."""
    setlist = list(set(linklist))             # Ditch duplicates
    sortedlist = sort_rank(setlist)           # Arrange by alexa rank
    sortedlist.reverse()                      # Reverse to have least common first
    check_them = sortedlist[:NUM_INTERESTING] # Grab NUM_INTERESTING of the most interesting-looking
    checked = sort_resolve(check_them)        # Go get rid of the bad (uninteresting) ones
    checked.reverse()                         # Sort with most uncommon first
    return checked



if __name__ == "__main__":
    LINKS = getlinks()
    BEST = mostinteresting(LINKS)
    for interesting_link in BEST:
        print(interesting_link)
