import requests
import requests_mock
from requests_mock import adapter
from operator import add
from functools import reduce

import stars

session = requests.Session()
adapter = requests_mock.Adapter()
session.mount('mock://', adapter)
url = 'https://api.github.com/orgs/nobody/repos'


def test_rate_limit():
    adapter.register_uri('GET', url, status_code='403')
    pass


def test_header_link():
    adapter.register_uri('GET', url,
        headers={
            'link':
                '<https://api.github.com/organizations/9919/repos?page=11>;'
                'rel="prev", <https://api.github.com/organizations/9919/repos?page=13>;'
                'rel="next", <https://api.github.com/organizations/9919/repos?page=14>;'
                'rel="last", <https://api.github.com/organizations/9919/repos?page=1>;'
                'rel="first'
            }
        )
    next = stars.get_next()


def test_stars_count():
    stars_list = [32, 64, 128, 256, 512, 1024, 2048, 4096, 8196]
    stars_total = reduce(add, stars_list)
    adapter.register_uri('GET', url, json={[{"stargazers_count": 1029}]})