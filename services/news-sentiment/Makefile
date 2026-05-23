download-historical-news:
	./download_historical_news.sh

dataset:
	uv run src/news_sentiment/dataset.py \
    --input_news data/cryptopanic_news.csv \
    --dataset_name news-sentiment-dataset-live \
    --samples 10 \
    --teacher_model claude-sonnet-4-5-20250929

tricky-example:
	uv run src/news_sentiment/dataset.py \
    --input_news "Ahmed thinks that Goldman Sacks will buy 1B BTC, and sell 1B ETH" \
    --dataset_name news-sentiment-dataset-live \
    --teacher_model claude-opus-4-20250514
