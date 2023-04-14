import pytest
from crawler import Crawler


@pytest.fixture
async def crawler():
    domain = "httpbin.org"
    yield Crawler(domain)


@pytest.mark.asyncio
async def test_request_not_found(crawler):
    async for c in crawler:
        url = "https://httpbin.org/status/404"
        response = await c._request(url)
        assert response is ""


@pytest.mark.asyncio
async def test_request_successful(crawler):
    async for c in crawler:
        url = "https://httpbin.org/delay/get"
        response = await c._request(url)
        assert response is not None


@pytest.mark.asyncio
async def test_request_timeout(crawler):
    async for c in crawler:
        url = "https://httpbin.org/delay/60"
        response = await c._request(url)
        assert response is None
