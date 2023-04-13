# Async Crawler

An async web crawler that can fetch all internal links from a given domain in parallel using asyncio and httpx.

## Usage

First, import the `Crawler` class:

```python
from crawler import Crawler
```

Next, instantiate the `Crawler` class by passing in the domain you want to crawl:

```python
crawler = Crawler(domain=<example.com>)
```

You can also specify the maximum number of workers to use:

```python
crawler = Crawler(domain='example.com', max_worker_count=10)
```

Start the crawler by calling the `start` method:

```python
 crawler.start()
```

## Configuration

The `Crawler` class has a few configurable parameters that you can use to tweak the crawler's behavior.

### `max_worker_count`

Specifies the maximum number of workers to use. Defaults to 10.

### `sleep_time`

Specifies the sleep time in seconds to add between each request. Defaults to 0.1.

### `must_handle_urls`

A set containing URLs that the crawler was not able to process.
Those are must look urls can have issues to fix.
### `visited_urls`

A set containing URLs that the crawler has already visited.

### `skipped_urls`

A set containing URLs that the crawler has skipped.
