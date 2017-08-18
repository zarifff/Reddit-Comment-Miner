# Reddit-Comment-Miner
Simple bot to analyze and extract comments from Reddit

Uses PRAW as a wrapper. Required import

You can use a reddit instance using your own credentials, or use PRAW reddit instance if you don't need to interact with the account. Reddit API keys can be found in settings -> apps

Use your own praw.ini file to set credentials, or hardcode it in the source code

Bot has 3 options for now.
- Can extract all comments in a submission
- Can extract all comments from a single or multiple subreddit(s) from specified number of 'hot' topics
- Can run indefinitely to extract new comments in stream.

All data dumps are in json format.
