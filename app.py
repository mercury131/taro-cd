import json
import random
import os
from datetime import datetime
import math
import requests
from flask import Flask, jsonify, request

app = Flask(__name__)

# Конфигурация микросервисов
SENTIMENT_API = os.getenv('SENTIMENT_API_URL')
TWITTER_SCRAPER = os.getenv('TWITTER_SCRAPER_URL')
USE_LLAMA = os.getenv('USE_LLAMA', 'false').lower() == 'true'

class MoonPhaseCalculator:
    @staticmethod
    def calculate(jd):
        phase = (jd - 2451550.1) / 29.530588853
        phase -= math.floor(phase)
        return phase * 100

def get_moon_phase():
    now = datetime.now()
    jd = now.toordinal() + 1721425 + 0.5
    return MoonPhaseCalculator.calculate(jd)

def load_tarot_cards(file_path):
    with open(file_path, 'r') as file:
        return json.load(file)

def get_zwl_rate():
    try:
        response = requests.get('https://a.success.africa/api/rates/fx-rates', timeout=3)
        return response.json()['rates']['Cash']
    except Exception as e:
        app.logger.error(f"ZWL rate error: {str(e)}")
        return 800

def analyze_sentiment(text):
    if not SENTIMENT_API or not USE_LLAMA:
        return 0
    try:
        response = requests.post(
            f"{SENTIMENT_API}/analyze",
            json={'text': text},
            timeout=10
        )
        return response.json().get('sentiment', 0)
    except Exception as e:
        app.logger.error(f"Sentiment analysis error: {str(e)}")
        return 0

def get_tweets(username):
    if not TWITTER_SCRAPER:
        return []
    try:
        response = requests.get(
            f"{TWITTER_SCRAPER}/tweets?username={username}",
            timeout=15
        )
        return response.json().get('tweets', [])
    except Exception as e:
        app.logger.error(f"Twitter scraper error: {str(e)}")
        return []

def calculate_scores(tarot_cards, drawn_cards):
    positive = 0
    negative = 0
    for card in drawn_cards:
        orientation = random.choice(['upright', 'reversed'])
        if orientation == 'upright':
            positive += tarot_cards[card]['upright_value']
            negative += tarot_cards[card]['reversed_value']
        else:
            positive += tarot_cards[card]['reversed_value']
            negative += tarot_cards[card]['upright_value']
    return positive, negative

@app.route('/draw', methods=['POST'])
def get_tarot_reading():
    data = request.get_json()
    num_cards = data.get('num_cards', 5)
    user_info = data.get('user_info', {})
    
    # Расчет базовых факторов
    moon_phase = get_moon_phase()
    zwl_rate = get_zwl_rate()
    is_oleg = 'олег' in user_info.get('name', '').lower()
    is_friday_eve = datetime.now().weekday() == 4 and datetime.now().hour >= 18
    
    # Анализ твитов
    musk_tweets = get_tweets('elonmusk')
    dasha_tweets = get_tweets('dasha_koreyka')
    combined_tweets = musk_tweets + dasha_tweets
    
    # Анализ сентимента
    sentiment_score = analyze_sentiment("\n".join(combined_tweets)) if combined_tweets else 0
    
    # Расчет карт
    tarot_cards = load_tarot_cards('tarot_cards.json')
    drawn_cards = random.sample(list(tarot_cards.keys()), num_cards)
    positive, negative = calculate_scores(tarot_cards, drawn_cards)
    
    # Расчет финального результата
    final_score = (positive - negative) * 0.5
    final_score += moon_phase * 0.1
    final_score += zwl_rate * 0.05
    final_score += sentiment_score * 0.3
    
    if is_oleg:
        final_score *= 0.4
    if is_friday_eve:
        final_score -= 20
        
    response = {
        'reading': 'good' if final_score >= 50 else 'bad',
        'num_cards': num_cards,
        'drawn_cards': ', '.join(drawn_cards),
        'factors': {
            'moon_phase': round(moon_phase, 2),
            'zwl_rate': zwl_rate,
            'sentiment_score': round(sentiment_score, 2),
            'oleg_effect': is_oleg,
            'friday_evening': is_friday_eve
        }
    }
    return jsonify(response)

@app.route('/cards', methods=['GET'])
def get_all_cards():
    return jsonify(load_tarot_cards('tarot_cards.json'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
