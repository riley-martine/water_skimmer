from bs4 import BeautifulSoup
import urllib.request
from urllib.parse import urlparse
import os.path
import os
import random
import tldextract

SEEDS = [
    "https://news.ycombinator.com/",
    "https://news.ycombinator.com/newest",
    "https://www.reddit.com/r/all/",
    "https://www.reddit.com/r/all/new",
    "http://usefulinterweb.com/",
    "http://popurls.com/",
    "http://www.jimmyr.com/",
    "http://www.metafilter.com/",
    "http://metanews.com/",
    "http://txchnologist.com/",
    "https://wordpress.org/showcase/",
    "http://slatestarcodex.com/",
    "http://sidebar.io/",
    "https://slashdot.org/",
    "http://digg.com/",
    "https://voat.co/v/all",
    "https://voat.co/v/all/new",
    "https://www.newsvine.com",
    "https://flipboard.com/",
    "http://www.fark.com/",
    # Since we exclude links containing "wikipedia"
    # we only get external links.
    # Run this a few times so we get more variety.
    "https://en.wikipedia.org/wiki/Special:Random",
    "https://en.wikipedia.org/wiki/Special:Random",
    "https://en.wikipedia.org/wiki/Special:Random",
    "https://en.wikipedia.org/wiki/Special:Random",
    "https://en.wikipedia.org/wiki/Special:Random",
    "https://en.wikipedia.org/wiki/Special:Random",
    "https://en.wikipedia.org/wiki/Special:Random",
]

# Where links are stored
LINKFILE = "links.txt"


# TODO Async requests
# TODO Open in Browser
# TODO Deal with timeouts (websites taking too long to respond) better
# TODO Stop incentivizing websites with a lot of self links
# TODO NCurses magic
# TODO Preserve at least some links from previous iteration
# TODO Handle getting 0 successful connections
# TODO Add Error log
# TODO Make time delay lower
# TODO fix subdir weighting (e.g. codereview.stackexchange.com, login.website.com, yro.slashdot))
# TODO Figure out youtu.be 
# TODO Total refactor
# TODO never revisit domains

def domain(url):
    return tldextract.extract(url).domain

def get_links(base):

    o = urlparse(base)
    truncated_base = o.netloc + o.path
    truncated_base = (truncated_base[:75] + '..') if len(truncated_base) > 77 else truncated_base
    print("|| Getting links from " + truncated_base)
    try:
        local = urllib.request.urlopen(base)
        local_info = local.info()

        if local.info().get_content_maintype() !=  "text":
            return []

        local = local.read()
        soup = BeautifulSoup(local, 'html.parser')

        links = [link.get('href') for link in soup.find_all('a')]
        links = [link for link in links 
            if link and (link.startswith('http') or link.startswith('www'))]
        links = filter(lambda x: domain(x) != domain(base), links)
        print("|| Success!")
        return links
    except:
        print("X| Error.")
        return  []


def write_links(links):
    with open(LINKFILE, 'a+') as f:
        for link in links:
            f.write(link+'\n')
        

def reduce_links():
    with open(LINKFILE, 'r') as f:
        links = list(set(f.readlines()))

    random.shuffle(links)

    with open(LINKFILE, 'w') as f:
        for link in links[:50]:
            f.write(link + '\n')
        

def is_good_link(link):
    sad_endings = ['gif', 'pdf', 'jpg', 'gifv', 'png', 'mp3', 'mp4']
    for ending in sad_endings:
        if link.endswith(ending):
            return False

     
    bad_websites = ['youtube', 'google', 'reddit', 'amazon', 'wikipedia', 'facebook', 'twitter']
    for text in bad_websites:
        if text in link:
            return False

    return True

def iterate_links():
    with open(LINKFILE, 'r') as f:
        links = [link.strip() for link in f.readlines() if link is not '\n']

    links = filter(is_good_link, links)
        

    linked = []
    for source in links:
        for destination in get_links(source):
            linked.append(destination)

    linked = list(set(linked))
    random.shuffle(linked)

    with open(LINKFILE, 'w') as f:
        for link in linked[:50]:
            f.write(link+'\n')
        

def make_me_a_file():
    print("Seeding...")
    for seed in SEEDS:
        write_links(get_links(seed))
    print("Done seeding.")
    reduce_links()

    for i in range(0,5):
        iterate_links()
        print("Iteration {} complete".format(i))




if __name__ == "__main__":
    for file_num in range(1, 21):
        make_me_a_file()
        os.rename(LINKFILE, str(file_num).zfill(2) + LINKFILE)
