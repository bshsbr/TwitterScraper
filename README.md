# Twitter Scraper with Time Filtering

A clean and simple Twitter scraper that supports time-based filtering. This tool allows you to scrape tweets from any Twitter user with precise time control.

## Features

- ✅ **Time Filtering**: Filter tweets by specific date ranges
- ✅ **Clean Output**: Includes tweet ID, text, date, and time
- ✅ **Export Support**: Save results to JSON or CSV files
- ✅ **Retry Logic**: Automatic retry on failures
- ✅ **Rate Limit Handling**: Built-in rate limit protection
- ✅ **Simple API**: Easy-to-use functions

## Installation

1. **Install Python dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Prepare your cookie file:**
   - Follow the [Setup Guide](SETUP_GUIDE.md) to get your Twitter cookies
   - Create a JSON file with your authentication cookies
   - See `example_cookies.json` for the expected format

## Quick Start

### Class-Based Usage (Recommended)

```python
import asyncio
from x_com_scraper import TwitterScraper

async def main():
    # Initialize scraper with custom settings
    scraper = TwitterScraper(
        cookie_file="your_cookies.json",  # Your cookie file
        rate_limit_delay=2.0,  # 2 seconds between requests
        retry_count=3,
        retry_delay=5
    )
    
    # Single user scraping
    tweets = await scraper.scrape_tweets(
        user_identifier="elonmusk",
        max_tweets=10
    )
    
    for tweet in tweets:
        print(f"[{tweet['time']}] {tweet['text'][:100]}...")

asyncio.run(main())
```

### Multi-User Scraping

```python
import asyncio
from x_com_scraper import TwitterScraper

async def main():
    scraper = TwitterScraper(rate_limit_delay=3.0)
    
    # Scrape from multiple users with rate limiting
    users = ["elonmusk", "OpenAI", "sama"]
    all_tweets = await scraper.scrape_multiple_users(
        user_identifiers=users,
        max_tweets_per_user=5,
        export_json_file="all_tweets.json"
    )
    
    print(f"Scraped {len(all_tweets)} tweets from {len(users)} users")

asyncio.run(main())
```

### Function-Based Usage (Legacy)

```python
import asyncio
from x_com_scraper import scrape_tweets

async def main():
    # Scrape recent tweets
    tweets = await scrape_tweets(
        user_identifier="elonmusk",
        max_tweets=10,
        cookie_file="your_cookies.json"  # Your cookie file
    )
    
    for tweet in tweets:
        print(f"[{tweet['time']}] {tweet['text'][:100]}...")

asyncio.run(main())
```

### Time Filtering Examples

#### 1. Filter by Date Range (Easy)
```python
from x_com_scraper import scrape_tweets_in_date_range

# Scrape tweets from January 1-31, 2024
tweets = await scrape_tweets_in_date_range(
    user_identifier="elonmusk",
    start_date="2024-01-01",
    end_date="2024-01-31",
    max_tweets=50,
    cookie_file="your_cookies.json"  # Your cookie file
)
```

#### 2. Filter by ISO Time (Precise)
```python
# Scrape tweets from specific time period
tweets = await scrape_tweets(
    user_identifier="elonmusk",
    start_time="2024-01-01T00:00:00Z",  # From January 1, 2024
    end_time="2024-12-31T23:59:59Z",    # To December 31, 2024
    max_tweets=100,
    cookie_file="your_cookies.json"  # Your cookie file
)
```

#### 3. Recent Tweets Only
```python
from datetime import datetime, timedelta

# Get tweets from last 7 days
end_date = datetime.now().strftime('%Y-%m-%d')
start_date = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')

tweets = await scrape_tweets_in_date_range(
    user_identifier="elonmusk",
    start_date=start_date,
    end_date=end_date,
    max_tweets=50,
    cookie_file="your_cookies.json"  # Your cookie file
)
```

## API Reference

### `TwitterScraper` Class

Main class for Twitter scraping with rate limiting and multi-user support.

#### Constructor Parameters:
- `cookie_file` (str): Path to your cookie file (default: "your_cookies.json")
- `username` (str): Your account username (default: "BashirSaburi")
- `rate_limit_delay` (float): Delay between requests in seconds (default: 2.0)
- `retry_count` (int): Number of retries for failed requests (default: 3)
- `retry_delay` (int): Delay between retries in seconds (default: 5)

#### Methods:

##### `scrape_tweets()`
Scrape tweets for a single user with time filtering.

**Parameters:**
- `user_identifier` (str|int): Username or Twitter ID
- `start_time` (str, optional): UTC start time in ISO 8601 format (inclusive)
- `end_time` (str, optional): UTC end time in ISO 8601 format (exclusive)
- `max_tweets` (int, optional): Maximum number of tweets to scrape
- `export_json_file` (str, optional): Path to export JSON file
- `export_csv_file` (str, optional): Path to export CSV file
- `show_preview` (bool): Whether to show preview (default: True)

**Returns:**
List of dictionaries with keys: `tweet_id`, `text`, `date`, `time`, `user_identifier`

##### `scrape_multiple_users()`
Scrape tweets for multiple users with rate limiting.

**Parameters:**
- `user_identifiers` (List[Union[str, int]]): List of usernames or Twitter IDs
- `start_time` (str, optional): UTC start time in ISO 8601 format (inclusive)
- `end_time` (str, optional): UTC end time in ISO 8601 format (exclusive)
- `max_tweets_per_user` (int, optional): Maximum number of tweets to scrape per user
- `export_json_file` (str, optional): Path to export JSON file
- `export_csv_file` (str, optional): Path to export CSV file
- `show_preview` (bool): Whether to show preview (default: True)

**Returns:**
List of dictionaries with keys: `tweet_id`, `text`, `date`, `time`, `user_identifier`

##### `scrape_tweets_in_date_range()`
Convenience method for date range filtering (single user).

**Parameters:**
- `user_identifier` (str|int): Username or Twitter ID
- `start_date` (str): Start date in YYYY-MM-DD format (inclusive)
- `end_date` (str): End date in YYYY-MM-DD format (inclusive)
- `max_tweets` (int, optional): Maximum number of tweets to scrape
- `**kwargs`: Additional arguments passed to `scrape_tweets()`

##### `scrape_multiple_users_in_date_range()`
Convenience method for date range filtering (multiple users).

**Parameters:**
- `user_identifiers` (List[Union[str, int]]): List of usernames or Twitter IDs
- `start_date` (str): Start date in YYYY-MM-DD format (inclusive)
- `end_date` (str): End date in YYYY-MM-DD format (inclusive)
- `max_tweets_per_user` (int, optional): Maximum number of tweets to scrape per user
- `**kwargs`: Additional arguments passed to `scrape_multiple_users()`

### Legacy Functions (Backward Compatibility)

#### `scrape_tweets()`

Main function to scrape tweets with time filtering.

**Parameters:**
- `user_identifier` (str|int): Username or Twitter ID
- `start_time` (str, optional): UTC start time in ISO 8601 format (inclusive)
- `end_time` (str, optional): UTC end time in ISO 8601 format (exclusive)
- `max_tweets` (int, optional): Maximum number of tweets to scrape
- `cookie_file` (str): Path to your cookie file (default: "your_cookies.json")
- `username` (str): Your account username (default: "BashirSaburi")
- `export_json_file` (str, optional): Path to export JSON file
- `export_csv_file` (str, optional): Path to export CSV file
- `show_preview` (bool): Whether to show preview (default: True)
- `retry_count` (int): Number of retries (default: 3)
- `retry_delay` (int): Delay between retries in seconds (default: 5)

**Returns:**
List of dictionaries with keys: `tweet_id`, `text`, `date`, `time`

#### `scrape_tweets_in_date_range()`

Convenience function for date range filtering.

**Parameters:**
- `user_identifier` (str|int): Username or Twitter ID
- `start_date` (str): Start date in YYYY-MM-DD format (inclusive)
- `end_date` (str): End date in YYYY-MM-DD format (inclusive)
- `max_tweets` (int, optional): Maximum number of tweets to scrape
- `**kwargs`: Additional arguments passed to `scrape_tweets()`

## Output Format

Each tweet is returned as a dictionary:

```python
{
    "tweet_id": "1953872175297184166",
    "text": "It's awesome! Try doing it with your younger kids...",
    "date": "2025-01-10T15:30:00+00:00",
    "time": "2025-01-10 15:30:00 UTC",
    "user_identifier": "elonmusk"  # Only in multi-user scraping
}
```

## Export Options

### JSON Export
```python
tweets = await scrape_tweets(
    user_identifier="elonmusk",
    max_tweets=50,
    export_json_file="tweets.json",
    cookie_file="your_cookies.json"  # Your cookie file
)
```

### CSV Export
```python
tweets = await scrape_tweets(
    user_identifier="elonmusk",
    max_tweets=50,
    export_csv_file="tweets.csv",
    cookie_file="your_cookies.json"  # Your cookie file
)
```

## Cookie File Format

Your cookie file should be a JSON file containing Twitter authentication cookies:

```json
{
    "auth_token": "your_auth_token_here",
    "ct0": "your_ct0_token_here",
    "__cf_bm": "your_cf_bm_token_here",
    "att": "your_att_token_here",
    "d_prefs": "your_d_prefs_here"
}
```

## Error Handling

The scraper includes built-in error handling:
- Automatic retry on failures
- Rate limit detection
- Account validation
- Database corruption prevention

## Examples

### Example 1: Basic Scraping (Class-based)
```python
scraper = TwitterScraper()
tweets = await scraper.scrape_tweets("elonmusk", max_tweets=10)
```

### Example 2: Multi-User Scraping with Rate Limiting
```python
scraper = TwitterScraper(rate_limit_delay=3.0)
users = ["elonmusk", "OpenAI", "sama"]
all_tweets = await scraper.scrape_multiple_users(
    user_identifiers=users,
    max_tweets_per_user=5,
    export_json_file="all_tweets.json"
)
```

### Example 3: Time Filtered Scraping (Multiple Users)
```python
scraper = TwitterScraper()
users = ["elonmusk", "OpenAI"]
tweets = await scraper.scrape_multiple_users_in_date_range(
    user_identifiers=users,
    start_date="2024-01-01",
    end_date="2024-12-31",
    max_tweets_per_user=20
)
```

### Example 4: Export to Files
```python
scraper = TwitterScraper()
tweets = await scraper.scrape_tweets(
    "elonmusk",
    max_tweets=50,
    export_json_file="elon_tweets.json",
    export_csv_file="elon_tweets.csv"
)
```

### Example 5: Custom Rate Limiting
```python
# Aggressive scraping (1 second between users)
scraper = TwitterScraper(rate_limit_delay=1.0)

# Conservative scraping (5 seconds between users)
scraper = TwitterScraper(rate_limit_delay=5.0)
```

## Troubleshooting

### Common Issues

1. **"No active accounts" error:**
   - Check your cookie file is valid
   - Ensure cookies are not expired
   - Try refreshing your Twitter session

2. **Rate limiting:**
   - The scraper automatically retries
   - Wait a few minutes between large requests
   - Use smaller `max_tweets` values

3. **User not found:**
   - Verify the username is correct
   - Check if the account is private
   - Try using Twitter ID instead of username

### Getting Help

If you encounter issues:
1. Check your cookie file format
2. Verify your internet connection
3. Ensure you're not being rate limited
4. Try with a smaller number of tweets first

## License

This project is for educational purposes. Please respect Twitter's terms of service and rate limits.

## Disclaimer

This tool is for educational and research purposes only. Users are responsible for complying with Twitter's terms of service and applicable laws.
