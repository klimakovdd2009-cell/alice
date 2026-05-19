# импортируем библиотеки
import os
from flask import Flask, request, jsonify
import logging
from waitress import serve

app = Flask(__name__)

logging.basicConfig(level=logging.INFO)

sessionStorage = {}


@app.route('/')
def health_check():
    return ''


@app.route('/post', methods=['POST'])
def main():
    logging.info(f'Request: {request.json!r}')

    response = {
        'session': request.json['session'],
        'version': request.json['version'],
        'response': {
            'end_session': False
        }
    }

    handle_dialog(request.json, response)

    logging.info(f'Response:  {response!r}')

    return jsonify(response)


def handle_dialog(req, res):
    user_id = req['session']['user_id']

    if user_id not in sessionStorage:
        sessionStorage[user_id] = {
            'current_animal': 'слон',
            'suggests': [
                "Не хочу.",
                "Не буду.",
                "Отстань!",
            ]
        }

    session = sessionStorage[user_id]

    if req['session']['new']:
        session['current_animal'] = 'слон'
        res['response']['text'] = 'Привет! Купи слона!'
        res['response']['buttons'] = get_suggests(user_id)
        return

    user_utterance = req['request']['original_utterance'].lower().strip()

    positive_keywords = ['куплю', 'покупаю', 'хорошо', 'ладно']

    if any(keyword in user_utterance for keyword in positive_keywords):
        current_animal = session['current_animal']
        res['response']['text'] = f'{current_animal.capitalize()} можно найти на Яндекс.Маркете!\n\nА теперь купи кролика!'

        session['current_animal'] = 'кролика'
        sessionStorage[user_id] = session

        res['response']['end_session'] = False
        res['response']['buttons'] = get_suggests(user_id)
        return

    current_animal = session['current_animal']
    res['response']['text'] = \
        f"Все говорят '{req['request']['original_utterance']}', а ты купи {current_animal}!"
    res['response']['buttons'] = get_suggests(user_id)


def get_suggests(user_id):
    session = sessionStorage[user_id]

    suggests = [
        {'title': suggest, 'hide': True}
        for suggest in session['suggests'][:2]
    ]

    session['suggests'] = session['suggests'][1:]
    sessionStorage[user_id] = session

    if len(suggests) < 2:
        suggests.append({
            "title": "Ладно",
            "url": "https://market.yandex.ru/search?text=слон",
            "hide": True
        })

    return suggests


if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    serve(app, host='127.0.0.1', port=port)
    # app.run()
