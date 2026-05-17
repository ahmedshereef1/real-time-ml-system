from datetime import datetime
from typing import List, Optional, Tuple

import requests
from loguru import logger
from pandas import Timestamp
from pydantic import BaseModel

CRYPTO_KEYWORDS = {
    'bitcoin',
    'ethereum',
    'solana',
    'xrp',
    'btc',
    'eth',
    'sol',
    'crypto',
    'blockchain',
}


class News(BaseModel):
    """
    This is the data model for the news.
    """

    id: int
    title: str
    description: Optional[str] = ''
    published_at: str  # "2024-12-18T12:29:27Z"
    created_at: str  # "2024-12-18T12:29:27Z"

    # Challenge: You can also keep the URL and scrape it to get even more context
    # about this piece of news.

    @classmethod
    def from_csv_row(
        cls,
        title: str,
        source_id: int,
        news_datetime: Timestamp,
    ) -> 'News':
        """
        This method is used to create a News object from a CSV row.

        The data we get from the CSV is in the following format:
        - title
        - sourceId
        - newsDatetime: pandas Timestamp
        """
        # Convert pandas Timestamp to UTC and format as ISO string with Z
        published_at = (
            news_datetime.tz_localize('UTC').isoformat().replace('+00:00', 'Z')
        )

        # convert the source_id into a string
        source = str(source_id)

        return cls(
            title=title,
            source=source,
            published_at=published_at,
        )

    def to_dict(self) -> dict:
        return {
            **self.model_dump(),
            'timestamp_ms': int(
                datetime.fromisoformat(
                    self.published_at.replace('Z', '+00:00')
                ).timestamp()
                * 1000
            ),
        }


class NewsDownloader:
    """
    This class is used to download news from the NewsData.io API.
    Free plan: 200 credits/day, no billing required.
    Sign up at: https://newsdata.io
    Another website but need billing: Cryptopanic API.
    """

    CRYPTOCOMPARE_URL = 'https://min-api.cryptocompare.com/data/v2/news/'

    def __init__(self, cryptocompare_api_key: str):
        self.api_key = cryptocompare_api_key

    def get_news(self, max_pages: Optional[int] = None) -> List[News]:
        """
        Keeps on calling _get_batch_of_news until it gets an empty list
        or reaches max_pages. If max_pages is None, fetches all pages.
        """
        news: List[News] = []
        next_page = None
        page_count = 0

        while True:
            batch, next_page = self._get_batch_of_news(next_page)
            news += batch
            page_count += 1
            logger.debug(f'Fetched {len(batch)} news items')

            if not batch or not next_page:
                logger.debug('No more pages, stopping.')
                break
            if max_pages and page_count >= max_pages:
                logger.debug(f'Reached max_pages={max_pages}, stopping.')
                break

        # sort the news by published_at
        news.sort(key=lambda x: x.published_at, reverse=False)

        return news

    def _get_batch_of_news(
        self, last_ts: Optional[str]
    ) -> Tuple[List[News], Optional[str]]:
        """
        Fetches one page of news from CryptoCompare.

        Args:
            last_ts: Unix timestamp to fetch news older than this (for pagination).

        Returns:
            A tuple of (list of News, next last_ts for pagination or None).
        """
        headers = {'authorization': f'Apikey {self.api_key}'}
        params = {
            'lang': 'EN',
            'sortOrder': 'latest',
            'categories': 'BTC,ETH,SOL,XRP,Blockchain,Mining,Technology',
        }
        if last_ts is not None:
            params['lTs'] = last_ts  # fetch articles older than this timestamp

        try:
            response = requests.get(
                self.CRYPTOCOMPARE_URL, headers=headers, params=params
            )
            response.raise_for_status()
            data = response.json()
        except Exception as e:
            logger.error(f'Error fetching/parsing CryptoCompare news: {e}')
            return [], None

        if data.get('Type') != 100:
            logger.error(
                f'CryptoCompare API error: {data.get("Message", "Unknown error")}'
            )
            return [], None

        results = data.get('Data', [])

        news = []
        oldest_ts = None

        for item in results:
            title = (item.get('title') or '').lower()

            # filter: keep only articles mentioning crypto keywords
            if not any(keyword in title for keyword in CRYPTO_KEYWORDS):
                continue

            # CryptoCompare uses integer unix timestamps
            published_unix: int = item.get('published_on', 0)
            published_at = datetime.utcfromtimestamp(published_unix).strftime(
                '%Y-%m-%dT%H:%M:%SZ'
            )

            # track the oldest timestamp for pagination cursor
            if oldest_ts is None or published_unix < oldest_ts:
                oldest_ts = published_unix

            news.append(
                News(
                    id=item.get('id', abs(hash(item.get('title', ''))) % (10**9)),
                    title=item.get('title') or '',
                    description=item.get('body') or '',
                    published_at=published_at,
                    created_at=published_at,
                )
            )

        # if we got a full batch (50 items), there may be more pages
        next_last_ts = oldest_ts if len(results) == 50 else None

        return news, next_last_ts


if __name__ == '__main__':
    from news.config import config

    news_downloader = NewsDownloader(cryptocompare_api_key=config.cryptocompare_api_key)
    # limit to 2 pages for testing
    news = news_downloader.get_news(max_pages=2)

    for news_item in news:
        print(news_item.id)
        print(news_item.title)
        print(news_item.published_at)
        print(news_item.created_at)
        print('-' * 100)
