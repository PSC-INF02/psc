"""@file http.py
Making http and https requests, using requests.
example :

>>> url = http://conceptnet5.media.mit.edu/data/5.3/assoc/c/en/barack_obama?limit=3&filter=%2Fc%2Fen%2F
>>> print(make_http_request(url).json())
"""

import requests
from abstracter.util.settings import HTTP_PROXY,HTTPS_PROXY


def make_https_request(url):
	"""
	@param url An url.
	@return A query result, which can be for example transformed into JSON by : result.json().
	"""
    return requests.get(url,proxies=HTTPS_PROXY)

def make_http_request(url):
	"""
	@param url An url.
	@return A query result, which can be for example transformed into JSON by : result.json().
	"""
    return requests.get(url,proxies=HTTP_PROXY)

