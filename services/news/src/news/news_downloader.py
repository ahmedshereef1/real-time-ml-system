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
    """

    NEWSDATA_URL = 'https://newsdata.io/api/1/latest'

    def __init__(self, coinmarketcap_api_key: str):
        self.api_key = coinmarketcap_api_key

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
        self, next_page: Optional[str]
    ) -> Tuple[List[News], Optional[str]]:
        """
        Connects to the NewsData.io API and fetches one batch of news.

        Args:
            next_page: The pagination cursor token from the previous response.

        Returns:
            A tuple containing the list of news and the next page token.
        """
        params = {
            'apikey': self.api_key,
            'language': 'en',
            'prioritydomain': 'top',
            'q': 'bitcoin OR ethereum OR solana OR XRP OR BTC OR ETH OR SOL OR crypto',
            'category': 'technology',
        }
        if next_page:
            params['page'] = next_page

        try:
            response = requests.get(self.NEWSDATA_URL, params=params)
            response.raise_for_status()
            data = response.json()
        except Exception as e:
            logger.error(f'Error fetching/parsing NewsData.io news: {e}')
            return [], None

        results = data.get('results', [])

        # parse the API response into a list of News objects
        # filter by crypto keywords in title
        news = []
        for item in results:
            title = (item.get('title') or '').lower()
            if not any(keyword in title for keyword in CRYPTO_KEYWORDS):
                continue

            # newsdata uses a string article_id, convert to int
            article_id = abs(hash(item['article_id'])) % (10**9)

            # pubDate format: "2024-12-18 12:29:27" → ISO Z format
            published_raw = item.get('pubDate') or ''
            try:
                published_at = datetime.strptime(
                    published_raw, '%Y-%m-%d %H:%M:%S'
                ).strftime('%Y-%m-%dT%H:%M:%SZ')
            except Exception:
                published_at = published_raw

            news.append(
                News(
                    id=article_id,
                    title=item.get('title') or '',
                    description=item.get('description') or '',
                    published_at=published_at,
                    created_at=published_at,
                )
            )

        # extract the next page token from the API response
        next_page_token = data.get('nextPage')

        return news, next_page_token


if __name__ == '__main__':
    from news.config import config

    news_downloader = NewsDownloader(
        coinmarketcap_api_key=config.coinmarketcap_api_key,
    )
    news = news_downloader.get_news(max_pages=1)

    for news_item in news:
        print(news_item.id)
        print(news_item.title)
        print(news_item.published_at)
        print(news_item.created_at)
        print('-' * 100)
