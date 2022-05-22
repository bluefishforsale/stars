#! /usr/bin/env python3
import argparse
import requests
import re

from backoff import expo, on_exception, random_jitter
from ratelimit import RateLimitException, limits


ONE_MINUTE = 60
HEADERS = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}


class MyHttpException(Exception):
    def __init__(self, message):
        print(message)


def add_stars(res):
    stars = 0
    page_stars = [ int(x.get('stargazers_count')) for x in res.json() ]
    for num in page_stars:
        stars = stars + num
    return stars


def backoff_hdlr(details):
    pass
    """print ("Backing off {wait:0.1f} seconds after {tries} tries "
           "calling function {target.__name__}() with args {args} and kwargs "
           "{kwargs}".format(**details))
           """

def get_next(res):
    if res.json():
        if res.headers.get('link'):
            links = res.headers.get('link').split(',')
            link = "".join( [ x for x in links if 'next' in x] )

@on_exception( expo, (MyHttpException, RateLimitException),
    max_tries=1000, jitter=random_jitter, on_backoff=backoff_hdlr, max_time=ONE_MINUTE * 15)
@limits(calls=5, period=ONE_MINUTE)
def stars_and_next(url):
    null_return = (0, '')
    # print(f"requesting {url}")
    res = requests.get(url, headers=HEADERS)
    if res.status_code != 200:
        raise MyHttpException(f"API response: {res.status_code}")
    link = get_next(res)
    stars = add_stars(res)
    print(stars)
    if link:
        url = "".join( [ x for x in re.split('^.*\<(.*)\>.*$', link) if 'http' in x ] )
        return (stars, url)
    return null_return


def recurse_stars(all_stars, url):
    if url:
        all_stars += recurse_stars(*stars_and_next(url))
    elif not next:
        all_stars += stars_and_next(url)
    return all_stars


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-o", "--org", help="the github org name to count stars for",
        default="cloudflare"
    )
    return parser.parse_args()


if __name__ == '__main__':
    args = parse_args()
    org_url = f"https://api.github.com/orgs/{args.org}/repos"
    # org_url = 'https://api.github.com/organizations/9919/repos?page=13'
    total_stars = 0
    print(f"Total stars: {recurse_stars(*stars_and_next(org_url)):,}")