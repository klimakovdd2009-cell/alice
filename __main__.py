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

    if req['session']['new']:
        sessionStorage[user_id] = {
            'stage': 'elephant',  # начальный этап — слон
            'suggests': [
                "Не хочу.",
                "Не буду.",
                "Отстань!",
            ]
        }
        res['response']['text'] = 'Привет! Купи слона!'
        res['response']['buttons'] = get_suggests(user_id)
        return

    session = sessionStorage[user_id]
    current_stage = session['stage']

    if current_stage == 'elephant':
        if req['request']['original_utterance'].lower() in [
            'ладно',
            'куплю',
            'покупаю',
            'хорошо',
            'я покупаю',
            'я куплю'
        ]:
            res['response']['text'] = 'Слона можно найти на Яндекс.Маркете! А теперь купи кролика — они отлично ладят!'
            session['stage'] = 'rabbit'  # переходим к этапу с кроликом
            res['response']['buttons'] = get_suggests(user_id)
            return
        else:
            res['response']['text'] = \
                f"Все говорят '{req['request']['original_utterance']}', а ты купи слона!"
            res['response']['buttons'] = get_suggests(user_id)
    elif current_stage == 'rabbit':
        if req['request']['original_utterance'].lower() in [
            'ладно',
            'куплю',
            'покупаю',
            'хорошо',
            'я покупаю',
            'я куплю'
        ]:
            res['response']['text'] = 'Кролика тоже можно найти на Яндекс.Маркете! Теперь у вас целая мини-зооферма! 😄 Хотите начать сначала?'
            res['response']['buttons'] = [
                {'title': 'Да, хочу!', 'hide': True},
                {'title': 'Нет, спасибо', 'hide': True}
            ]
            return
        else:
            res['response']['text'] = \
                f"Все говорят '{req['request']['original_utterance']}', а ты купи кролика!"
            res['response']['buttons'] = get_suggests(user_id)


def get_suggests(user_id):
    session = sessionStorage[user_id]
    stage = session['stage']

    suggests = [
        {'title': suggest, 'hide': True}
        for suggest in session['suggests'][:2]
    ]

    session['suggests'] = session['suggests'][1:]
    sessionStorage[user_id] = session

    if len(suggests) < 2:
        if stage == 'elephant':
            suggests.append({
                "title": "Ладно",
                "url": "https://market.yandex.ru/search?text=слон",
                "hide": True
            })
        elif stage == 'rabbit':
            suggests.append({
                "title": "Ладно",
                "url": "https://market.yandex.ru/search?text=кролик",
                "hide": True
            })

    return suggests


if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    serve(app, host='127.0.0.1', port=port)
