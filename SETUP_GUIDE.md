# Setup Guide for Twitter Scraper

## 🔐 Getting Your Twitter Cookies

To use this scraper, you need to provide your Twitter authentication cookies. Here's how to get them:

### Method 1: Using Browser Developer Tools

1. **Open Twitter** in your browser and log in
2. **Open Developer Tools** (F12 or right-click → Inspect)
3. **Go to Network tab**
4. **Refresh the page** or navigate to any Twitter page
5. **Find any request** to `twitter.com` in the network tab
6. **Right-click the request** → Copy → Copy as cURL
7. **Look for the `Cookie:` header** in the cURL command
8. **Extract the cookie values** and create a JSON file

### Method 2: Using Browser Extensions

1. **Install a cookie export extension** like "Cookie Editor" for Chrome/Firefox
2. **Go to Twitter** and log in
3. **Open the extension** and export cookies
4. **Save as JSON** file

### Method 3: Manual Extraction

1. **Go to Twitter** and log in
2. **Open Developer Tools** → Application tab → Cookies
3. **Find the following cookies** and copy their values:
   - `auth_token`
   - `ct0`
   - `__cf_bm`
   - `att`
   - `d_prefs`
   - `guest_id`

## 📁 Creating Your Cookie File

Create a file named `your_cookies.json` with this structure:

```json
{
  "auth_token": "your_actual_auth_token_here",
  "ct0": "your_actual_ct0_token_here",
  "__cf_bm": "your_actual_cf_bm_token_here",
  "att": "your_actual_att_token_here",
  "d_prefs": "your_actual_d_prefs_here",
  "guest_id": "your_actual_guest_id_here"
}
```

## ⚠️ Security Important Notes

- **Never share your cookie file** - it contains your authentication tokens
- **Don't commit cookies to Git** - they're automatically ignored by `.gitignore`
- **Refresh cookies regularly** - they expire and need to be updated
- **Use a dedicated account** - consider using a separate Twitter account for scraping

## 🚀 Quick Start

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Create your cookie file** (see above)

3. **Run the scraper:**
   ```python
   import asyncio
   from x_com_scraper import TwitterScraper
   
   async def main():
       scraper = TwitterScraper(cookie_file="your_cookies.json")
       tweets = await scraper.scrape_tweets("elonmusk", max_tweets=5)
       print(f"Scraped {len(tweets)} tweets")
   
   asyncio.run(main())
   ```

## 🔄 Updating Cookies

When you get authentication errors, your cookies may have expired:

1. **Go to Twitter** and log in again
2. **Follow the steps above** to get fresh cookies
3. **Replace your cookie file** with the new values
4. **Try running the scraper again**

## 📞 Troubleshooting

- **"No active accounts" error**: Check your cookie file format and validity
- **"Invalid cookie value" error**: Some cookies may contain special characters that need cleaning
- **Rate limiting**: Wait a few minutes between requests or reduce the number of tweets
