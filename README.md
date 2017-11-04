# water Skimmer
Like a spider, but on the surface. Pulls from seed websites links  that do not link to the same domain, chooses 50 at random, repeats with new links.


## Usage
`pip3 install -r requirements.txt`

`python3 water_skimmer.py`

Program will run for 5 iterations, 20 times. Final links will be output to `links/XXXlinks.txt`, where XXX starts at 0 and increments up to 999. 20 files will be generated each time.

## Analyzing
After running `water_skimmer.py`, you probably want to see what kind of links it found for you. You can comb through these by hand, but I also wrote a tool to help find the interesting ones.

"Interesting" here is defined as the links whose domains (or rather, the domains of the URLs the links resolve to) being ranked as uncommon by the alexa top 1 million, or being unranked.

To find "interesting" URLs, run `python3 findinteresting.py`. This will run on all the URLs in all the files in the `links` directory, and print out the most interesting ones (up to 100).

## Todos
[ ] Add todos
