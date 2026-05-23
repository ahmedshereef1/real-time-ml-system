from opik import track

from news_sentiment.baml_client.sync_client import b
from news_sentiment.baml_client.types import SentimentScores


class SentimentExtractor:
    def __init__(self, model: str):
        self.model = model

    @track
    def extract_sentiment_scores(self, news: str) -> SentimentScores:
        """
        Extracts the sentiment scores for the given news.
        """
        return b.ExtractSentimentScores(news)


if __name__ == '__main__':
    sentiment_extractor = SentimentExtractor(model='CustomSonnet4')
    print(
        sentiment_extractor.extract_sentiment_scores(
            'Goldman Sachs is about to buy 1B in Bitcoin, and sell 1B in Ethereum.'
        )
    )
