#!/usr/bin/env python3
"""
Twitter Scraper with Time Filtering
A clean and simple Twitter scraper that supports time-based filtering
"""

import json
import asyncio
import csv
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Dict, Optional, Union
from twscrape import set_log_level, API

ISO_FMT = "%Y-%m-%dT%H:%M:%SZ"

class TwitterScraper:
    """
    A clean Twitter scraper class with time filtering and rate limiting support.
    """
    
    def __init__(
        self,
        cookie_file: str = "ehsan.json",
        username: str = "BashirSaburi",
        rate_limit_delay: float = 2.0,
        retry_count: int = 3,
        retry_delay: int = 5
    ):
        """
        Initialize the Twitter scraper.
        
        Args:
            cookie_file: Path to your cookie file
            username: Your account username
            rate_limit_delay: Delay between requests in seconds (default: 2.0)
            retry_count: Number of retries for failed requests (default: 3)
            retry_delay: Delay between retries in seconds (default: 5)
        """
        self.cookie_file = cookie_file
        self.username = username
        self.rate_limit_delay = rate_limit_delay
        self.retry_count = retry_count
        self.retry_delay = retry_delay
        self.api = None
    
    def _json_to_cookie_header(self, path: str | Path) -> str:
        """Convert JSON cookie file to cookie header string."""
        data = json.loads(Path(path).read_text(encoding="utf-8"))
        
        filtered_cookies = {}
        for k, v in data.items():
            # Skip problematic cookies
            if k in ['g_state'] or (isinstance(v, str) and ('{' in v or '}' in v)):
                continue
            
            # Clean string values
            if isinstance(v, str):
                cleaned_value = v.replace('"', '').strip()
                if cleaned_value and not cleaned_value.startswith('{'):
                    filtered_cookies[k] = cleaned_value
            else:
                filtered_cookies[k] = str(v)
        
        # Convert to cookie header string
        cookie_pairs = [f"{k}={v}" for k, v in filtered_cookies.items()]
        return "; ".join(cookie_pairs)
    
    def _to_dt(self, ts: Optional[str]) -> Optional[datetime]:
        """Convert ISO timestamp string to datetime object."""
        return (
            datetime.strptime(ts, ISO_FMT).replace(tzinfo=timezone.utc) if ts else None
        )
    
    async def _ensure_account_loaded(self):
        """Ensure account is loaded and ready"""
        # Always reset database to avoid corruption issues
        db_path = 'accounts.db'
        import os
        if os.path.exists(db_path):
            os.remove(db_path)
            print(f"🗑️ Reset account pool")
            await asyncio.sleep(0.5)  # Give more time for cleanup
        
        # Create new API instance
        self.api = API()
        set_log_level("DEBUG")
        
        # Load cookies and add account
        cookie_header = self._json_to_cookie_header(self.cookie_file)
        import uuid
        dummy = str(uuid.uuid4())
        
        try:
            await self.api.pool.add_account(
                self.username,
                dummy,  # password
                f"{dummy[:8]}@example.com",  # email
                dummy,  # email_password
                user_agent=(
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/124.0 Safari/537.36"
                ),
                cookies=cookie_header,
                proxy=None
            )
            print(f"✅ Account '{self.username}' added with {len(cookie_header.split(';'))} cookies")
            
            # Verify account is active
            await asyncio.sleep(0.1)  # Small delay to ensure account is properly added
            accounts = await self.api.pool.get_all()
            if accounts:
                print("✅ Account is active and ready")
                return True
            else:
                raise ValueError("No accounts found after adding")
                
        except Exception as e:
            print(f"⚠️ Account setup warning: {e}")
            return False
    
    async def _get_user_id(self, user_identifier: Union[str, int]) -> int:
        """Get user ID from username or return the ID if already provided."""
        if isinstance(user_identifier, str):
            print(f"🔍 Looking up user: @{user_identifier}")
            
            # Retry logic for user lookup
            user = None
            for attempt in range(self.retry_count):
                try:
                    accounts = await self.api.pool.get_all()
                    if not accounts:
                        raise ValueError("No accounts in pool")
                    
                    user = await self.api.user_by_login(user_identifier)
                    if user:
                        break
                    else:
                        raise ValueError(f"User @{user_identifier} not found")
                except Exception as e:
                    print(f"⚠️  Attempt {attempt + 1}/{self.retry_count} failed: {e}")
                    if attempt < self.retry_count - 1:
                        print(f"Retrying in {self.retry_delay} seconds...")
                        await asyncio.sleep(self.retry_delay)
                    else:
                        raise ValueError(f"Could not find user @{user_identifier} after {self.retry_count} attempts")
            
            user_id = user.id
            print(f"✅ Found user @{user_identifier} (ID: {user_id})")
            return user_id
        else:
            user_id = user_identifier
            print(f"✅ Using Twitter ID: {user_id}")
            return user_id
    
    async def scrape_tweets(
        self,
        user_identifier: Union[str, int],
        start_time: Optional[str] = None,
        end_time: Optional[str] = None,
        max_tweets: Optional[int] = None,
        export_json_file: Optional[str] = None,
        export_csv_file: Optional[str] = None,
        show_preview: bool = True
    ) -> List[Dict[str, str]]:
        """
        Scrape tweets for a single user with time filtering.
        
        Args:
            user_identifier: Username (string) or Twitter ID (integer)
            start_time: UTC start time in ISO 8601 format (inclusive)
            end_time: UTC end time in ISO 8601 format (exclusive)
            max_tweets: Maximum number of tweets to scrape
            export_json_file: Path to export JSON file
            export_csv_file: Path to export CSV file
            show_preview: Whether to show preview of tweets
        
        Returns:
            List of dictionaries containing tweet_id, text, date, and time
        """
        
        print(f"🚀 Starting Twitter scraper for: {user_identifier}")
        
        # Ensure account is loaded
        if not self.api:
            success = await self._ensure_account_loaded()
            if not success:
                raise ValueError("Failed to load account")
        
        # Get user ID
        user_id = await self._get_user_id(user_identifier)
        
        # Handle time filtering
        start_dt, end_dt = self._to_dt(start_time), self._to_dt(end_time)
        if start_dt:
            print(f"📅 Filtering tweets from: {start_dt}")
        if end_dt:
            print(f"📅 Filtering tweets until: {end_dt}")
        
        # Scrape tweets with retry logic
        tweets = []
        tweet_count = 0
        
        for attempt in range(self.retry_count):
            try:
                print(f"📥 Scraping tweets (attempt {attempt + 1}/{self.retry_count})")
                
                async for tw in self.api.user_tweets(user_id, limit=max_tweets):
                    # Apply time filtering
                    if start_dt and tw.date < start_dt:
                        print(f"⏰ Reached start time limit, stopping at tweet {tweet_count}")
                        break
                    if end_dt and tw.date > end_dt:
                        continue
                    
                    # Format date and time
                    tweet_date = tw.date.isoformat() if tw.date else None
                    tweet_time = tw.date.strftime("%Y-%m-%d %H:%M:%S UTC") if tw.date else None
                    
                    tweets.append({
                        "tweet_id": str(tw.id),
                        "text": tw.rawContent,
                        "date": tweet_date,
                        "time": tweet_time,
                        "user_identifier": user_identifier
                    })
                    tweet_count += 1
                    
                    if tweet_count % 10 == 0:
                        print(f"📈 Scraped {tweet_count} tweets...")
                    
                    if max_tweets and tweet_count >= max_tweets:
                        print(f"📊 Reached max tweets limit ({max_tweets})")
                        break
                
                # If we got here, scraping was successful
                break
                    
            except Exception as e:
                print(f"⚠️  Scraping attempt {attempt + 1} failed: {e}")
                if attempt < self.retry_count - 1:
                    print(f"Retrying in {self.retry_delay} seconds...")
                    await asyncio.sleep(self.retry_delay)
                else:
                    print(f"❌ Failed to scrape tweets after {self.retry_count} attempts")
                    break
        
        print(f"✅ Successfully scraped {len(tweets)} tweets")
        
        # Export if requested
        if export_json_file:
            with open(export_json_file, 'w', encoding='utf-8') as f:
                json.dump(tweets, f, ensure_ascii=False, indent=2)
            print(f"💾 Exported to JSON: {export_json_file}")
        
        if export_csv_file:
            with open(export_csv_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=['tweet_id', 'text', 'date', 'time', 'user_identifier'])
                writer.writeheader()
                writer.writerows(tweets)
            print(f"💾 Exported to CSV: {export_csv_file}")
        
        # Show preview if requested
        if show_preview and tweets and not (export_json_file or export_csv_file):
            print("\n📋 Tweet Preview:")
            for i, tweet in enumerate(tweets[:10]):
                text_preview = tweet['text'][:80] + ("..." if len(tweet['text']) > 80 else "")
                time_str = tweet['time'] if tweet['time'] else 'Unknown'
                tweet_id = tweet.get('tweet_id', 'Unknown')
                print(f"{i+1}. [{time_str}] ID: {tweet_id} | {text_preview}")
            if len(tweets) > 10:
                print(f"... and {len(tweets) - 10} more tweets")
        
        return tweets
    
    async def scrape_tweets_in_date_range(
        self,
        user_identifier: Union[str, int],
        start_date: str,  # Format: "YYYY-MM-DD"
        end_date: str,    # Format: "YYYY-MM-DD"
        max_tweets: Optional[int] = None,
        **kwargs
    ) -> List[Dict[str, str]]:
        """
        Scrape tweets within a date range for a single user.
        
        Args:
            user_identifier: Username (string) or Twitter ID (integer)
            start_date: Start date in YYYY-MM-DD format (inclusive)
            end_date: End date in YYYY-MM-DD format (inclusive)
            max_tweets: Maximum number of tweets to scrape
            **kwargs: Additional arguments passed to scrape_tweets
        
        Returns:
            List of dictionaries containing tweet_id, text, date, and time
        """
        # Convert dates to ISO format
        start_time = f"{start_date}T00:00:00Z"
        end_time = f"{end_date}T23:59:59Z"
        
        return await self.scrape_tweets(
            user_identifier=user_identifier,
            start_time=start_time,
            end_time=end_time,
            max_tweets=max_tweets,
            **kwargs
        )
    
    async def scrape_multiple_users(
        self,
        user_identifiers: List[Union[str, int]],
        start_time: Optional[str] = None,
        end_time: Optional[str] = None,
        max_tweets_per_user: Optional[int] = None,
        export_json_file: Optional[str] = None,
        export_csv_file: Optional[str] = None,
        show_preview: bool = True
    ) -> List[Dict[str, str]]:
        """
        Scrape tweets for multiple users with rate limiting.
        
        Args:
            user_identifiers: List of usernames (strings) or Twitter IDs (integers)
            start_time: UTC start time in ISO 8601 format (inclusive)
            end_time: UTC end time in ISO 8601 format (exclusive)
            max_tweets_per_user: Maximum number of tweets to scrape per user
            export_json_file: Path to export JSON file
            export_csv_file: Path to export CSV file
            show_preview: Whether to show preview of tweets
        
        Returns:
            List of dictionaries containing tweet_id, text, date, time, and user_identifier
        """
        
        print(f"🚀 Starting multi-user Twitter scraper for {len(user_identifiers)} users")
        print(f"⏱️  Rate limit delay: {self.rate_limit_delay} seconds between users")
        
        all_tweets = []
        
        for i, user_identifier in enumerate(user_identifiers, 1):
            print(f"\n{'='*50}")
            print(f"📱 Processing user {i}/{len(user_identifiers)}: {user_identifier}")
            print(f"{'='*50}")
            
            try:
                # Scrape tweets for this user
                tweets = await self.scrape_tweets(
                    user_identifier=user_identifier,
                    start_time=start_time,
                    end_time=end_time,
                    max_tweets=max_tweets_per_user,
                    show_preview=False  # Don't show preview for individual users
                )
                
                all_tweets.extend(tweets)
                print(f"✅ Added {len(tweets)} tweets from {user_identifier}")
                
                # Rate limiting delay between users (except for the last user)
                if i < len(user_identifiers):
                    print(f"⏳ Waiting {self.rate_limit_delay} seconds before next user...")
                    await asyncio.sleep(self.rate_limit_delay)
                
            except Exception as e:
                print(f"❌ Failed to scrape tweets for {user_identifier}: {e}")
                continue
        
        print(f"\n🎉 Multi-user scraping completed!")
        print(f"📊 Total tweets scraped: {len(all_tweets)} from {len(user_identifiers)} users")
        
        # Export if requested
        if export_json_file:
            with open(export_json_file, 'w', encoding='utf-8') as f:
                json.dump(all_tweets, f, ensure_ascii=False, indent=2)
            print(f"💾 Exported all tweets to JSON: {export_json_file}")
        
        if export_csv_file:
            with open(export_csv_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=['tweet_id', 'text', 'date', 'time', 'user_identifier'])
                writer.writeheader()
                writer.writerows(all_tweets)
            print(f"💾 Exported all tweets to CSV: {export_csv_file}")
        
        # Show preview if requested
        if show_preview and all_tweets and not (export_json_file or export_csv_file):
            print("\n📋 Tweet Preview (from all users):")
            for i, tweet in enumerate(all_tweets[:10]):
                text_preview = tweet['text'][:80] + ("..." if len(tweet['text']) > 80 else "")
                time_str = tweet['time'] if tweet['time'] else 'Unknown'
                user = tweet.get('user_identifier', 'Unknown')
                tweet_id = tweet.get('tweet_id', 'Unknown')
                print(f"{i+1}. [{time_str}] @{user} | ID: {tweet_id} | {text_preview}")
            if len(all_tweets) > 10:
                print(f"... and {len(all_tweets) - 10} more tweets")
        
        return all_tweets
    
    async def scrape_multiple_users_in_date_range(
        self,
        user_identifiers: List[Union[str, int]],
        start_date: str,  # Format: "YYYY-MM-DD"
        end_date: str,    # Format: "YYYY-MM-DD"
        max_tweets_per_user: Optional[int] = None,
        **kwargs
    ) -> List[Dict[str, str]]:
        """
        Scrape tweets within a date range for multiple users.
        
        Args:
            user_identifiers: List of usernames (strings) or Twitter IDs (integers)
            start_date: Start date in YYYY-MM-DD format (inclusive)
            end_date: End date in YYYY-MM-DD format (inclusive)
            max_tweets_per_user: Maximum number of tweets to scrape per user
            **kwargs: Additional arguments passed to scrape_multiple_users
        
        Returns:
            List of dictionaries containing tweet_id, text, date, time, and user_identifier
        """
        # Convert dates to ISO format
        start_time = f"{start_date}T00:00:00Z"
        end_time = f"{end_date}T23:59:59Z"
        
        return await self.scrape_multiple_users(
            user_identifiers=user_identifiers,
            start_time=start_time,
            end_time=end_time,
            max_tweets_per_user=max_tweets_per_user,
            **kwargs
        )

# Convenience functions for backward compatibility
async def scrape_tweets(
    user_identifier: Union[str, int],
    start_time: Optional[str] = None,
    end_time: Optional[str] = None,
    max_tweets: Optional[int] = None,
    cookie_file: str = "ehsan.json",
    username: str = "BashirSaburi",
    export_json_file: Optional[str] = None,
    export_csv_file: Optional[str] = None,
    show_preview: bool = True,
    retry_count: int = 3,
    retry_delay: int = 5
) -> List[Dict[str, str]]:
    """Backward compatibility function for single user scraping."""
    scraper = TwitterScraper(
        cookie_file=cookie_file,
        username=username,
        retry_count=retry_count,
        retry_delay=retry_delay
    )
    return await scraper.scrape_tweets(
        user_identifier=user_identifier,
        start_time=start_time,
        end_time=end_time,
        max_tweets=max_tweets,
        export_json_file=export_json_file,
        export_csv_file=export_csv_file,
        show_preview=show_preview
    )

async def scrape_tweets_in_date_range(
    user_identifier: Union[str, int],
    start_date: str,
    end_date: str,
    max_tweets: Optional[int] = None,
    **kwargs
) -> List[Dict[str, str]]:
    """Backward compatibility function for date range scraping."""
    scraper = TwitterScraper()
    return await scraper.scrape_tweets_in_date_range(
        user_identifier=user_identifier,
        start_date=start_date,
        end_date=end_date,
        max_tweets=max_tweets,
        **kwargs
    )

if __name__ == "__main__":
    async def main():
        print("Twitter Scraper with Time Filtering")
        print("=" * 40)
        
        try:
            # Example: Basic scraping with class
            scraper = TwitterScraper(
                cookie_file="ehsan.json",
                rate_limit_delay=2.0,  # 2 seconds between requests
                retry_count=3,
                retry_delay=5
            )
            
            # Single user scraping
            tweets = await scraper.scrape_tweets(
                user_identifier=1499585375534206980,
                max_tweets=5
            )
            
            print(f"\n🎉 Success! Scraped {len(tweets)} tweets using your account.")
            
            # Example: Multi-user scraping (commented out)
            # users = ["elonmusk", "OpenAI", "sama"]
            # all_tweets = await scraper.scrape_multiple_users(
            #     user_identifiers=users,
            #     max_tweets_per_user=3,
            #     export_json_file="multi_user_tweets.json"
            # )
            
        except Exception as e:
            print(f"❌ Error: {e}")
            print("This might be due to rate limiting. Try again later.")
    
    asyncio.run(main())
