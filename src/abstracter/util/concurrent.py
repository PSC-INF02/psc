"""@file concurrent.py
@brief Making concurrent requests, using asyncio and aiohttp.
"""

import asyncio
import aiohttp
import json
from abstracter.util.settings import PROXY

CONNECTOR = aiohttp.ProxyConnector(proxy=PROXY) if PROXY else None


@asyncio.coroutine
def fetch_page(tag, url, dict, parsing_method=None):
    """
    @param parsing_method A method to apply to a JSON result.

    @see abstracter.conceptnet5_client.result
    """
    response = yield from aiohttp.request(
        'GET', url,
        connector=CONNECTOR,
    )
    if response.status == 200:
        # print("data fetched successfully for: %s" % url)
        raw = yield from response.json()
        dict[tag] = parsing_method(raw) if parsing_method else raw
    else:
        print("data fetch failed for: %s" % url)
        print(response.content, response.status)


def requests(urls, parsing_method=None):
    """
    @param urls : a dict of tag : url
    @result A dict containing the query result, in JSON, for each url.
    """
    print("Launching " + len(urls).__str__() + " requests !")
    dict = {}
    loop = asyncio.get_event_loop()
    f = asyncio.wait([(fetch_page(tag, urls[tag], dict, parsing_method)) for tag in (urls)])
    loop.run_until_complete(f)
    print("Requests finished ! Returning " + len(dict).__str__() + " objects !")
    return dict
