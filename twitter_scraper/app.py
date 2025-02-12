from flask import Flask, jsonify, request
from requests_html import HTMLSession
import asyncio

app = Flask(__name__)
session = HTMLSession()

async def scrape_tweets(username):
    try:
        url = f"https://twitter.com/{username}"
        response = await session.get(url)
        await response.html.arender(timeout=20)
        
        tweets = []
        for item in response.html.find('article[data-testid="tweet"]'):
            tweet = item.find('div[data-testid="tweetText"]', first=True)
            if tweet:
                tweets.append(tweet.text)
        return tweets[:10]
    except Exception as e:
        print(f"Error: {str(e)}")
        return []

@app.route('/tweets', methods=['GET'])
def get_tweets():
    username = request.args.get('username')
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    tweets = loop.run_until_complete(scrape_tweets(username))
    return jsonify({'tweets': tweets})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5002)
