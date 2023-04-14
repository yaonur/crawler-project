import pytest
from crawler import Crawler


@pytest.mark.asyncio
async def test_filter_url():
    domain = "sample.com"
    wc = Crawler(domain)
    # dont think there will be anchor tag with www.sdfdsf.com without slash
    # maybe theres some cases like that
    # if so filter_url should be changed to handle that

    tests_list = [
        {"anchor": "https://sample.com/", "result": "https://sample.com/"},
        {"anchor": "/subpage", "result": "https://sample.com/subpage"},
        {"anchor": "subpage", "result": None},
        {"anchor": "https://www.sample.com", "result": "https://www.sample.com"},
        {"anchor": "//www.sample.com", "result": "https://www.sample.com"},
        {"anchor": "http://www.sample.com", "result": "http://www.sample.com"},
        {"anchor": "ftp://www.sample.com", "result": None},
        {"anchor": "sample", "result": None},
        {"anchor": "http://sample", "result": None},
        {"anchor": "http://.com", "result": None},
    ]

    for test in tests_list:
        result = await wc.filter_url(domain, test["anchor"])
        assert result == test["result"]
