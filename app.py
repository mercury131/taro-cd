import json
import random
from flask import Flask, jsonify, request

app = Flask(__name__)

def load_tarot_cards(file_path):
    with open(file_path, 'r') as file:
        return json.load(file)

tarot_cards=load_tarot_cards('tarot_cards.json')

@app.route('/draw', methods=['POST'])
def get_tarot_reading():
    data = request.get_json()
    num_cards = data.get('num_cards', 5)

    # Выбираем случайные уникальные карты
    # Определяем расклад на основе выбранных карт
    reading = determine_reading(num_cards, tarot_card_file='tarot_cards.json')

    response = {
        'reading': reading[0],
        'num_cards': num_cards,
        'drawn_cards': ', '.join(reading[1])
    }
    return jsonify(response)

@app.route('/cards', methods=['GET'])
def get_all_cards():
    return jsonify(tarot_cards)

def determine_reading(num_drawn_cards, tarot_card_file='tarot_cards.json'):
    # Загружаем карты из JSON файла
    tarot_cards = load_tarot_cards(tarot_card_file)

    # Выборка случайных карт
    drawn_cards = random.sample(list(tarot_cards.keys()), k=num_drawn_cards)

    positive_score = 0
    negative_score = 0

    for card in drawn_cards:
        card_data = tarot_cards[card]
        # Предполагаем, что ориентация будет определяться случайным образом
        orientation = random.choice(['upright', 'reversed'])

        if orientation == 'upright':
            positive_score += card_data['upright_value']
            negative_score += card_data['reversed_value']
        else:
            positive_score += card_data['reversed_value']
            negative_score += card_data['upright_value']

    if positive_score > negative_score:
        return 'good' , drawn_cards
    else:
        return 'bad' , drawn_cards

if __name__ == '__main__':
    app.run(debug=True)