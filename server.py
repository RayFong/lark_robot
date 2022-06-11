#!/usr/bin/env python3.8

import json
import os
import random
import logging
import requests
import re
from api import MessageApiClient
from event import MessageReceiveEvent, UrlVerificationEvent, EventManager
from flask import Flask, jsonify
from dotenv import load_dotenv, find_dotenv
from sim import *

from guess_idiom import IdiomGuesser

# load env parameters form file named .env
load_dotenv(find_dotenv())

app = Flask(__name__)

# load from env
APP_ID = os.getenv("APP_ID")
APP_SECRET = os.getenv("APP_SECRET")
VERIFICATION_TOKEN = os.getenv("VERIFICATION_TOKEN")
ENCRYPT_KEY = os.getenv("ENCRYPT_KEY")
LARK_HOST = os.getenv("LARK_HOST")

# init service
message_api_client = MessageApiClient(APP_ID, APP_SECRET, LARK_HOST)
event_manager = EventManager()

repo = QuestionRepository()
repo.load('data/chat.json')
robot = Robot(repo)


# 猜成语
guesser = IdiomGuesser('./data/idioms.json', 30)
idiom_hint = '请输入猜的成语及结果，如\\n qiao3 duo2 tian1 gong1, 331 133 331 331'

@event_manager.register("url_verification")
def request_url_verify_handler(req_data: UrlVerificationEvent):
    # url verification, just need return challenge
    if req_data.event.token != VERIFICATION_TOKEN:
        raise Exception("VERIFICATION_TOKEN is invalid")
    return jsonify({"challenge": req_data.event.challenge})


def render_guess_result(result, new_word, candidates=None):
    if len(result) == 0:
        if new_word:
            return '小机器人词库不足了，请输入`猜成语`重新开始吧'
        else:
            return '没有更多候选了~~~\\n' + idiom_hint

    if len(result) == 1 and new_word:
        return f'答案是: {result[0]}，猜成语游戏结束。你可以输入`猜成语`重新开始'

    total = ''
    if candidates:
        total = f'共有{len(candidates)}个, '

    if len(result) < 30:
        return total + f'推荐{len(result)}个: [' + ', '.join(result) + ']\\n' + idiom_hint
    else:
        return total + '推荐30个: [' + ', '.join(result) + ']\\n 输入`查看更多`，或者,' + idiom_hint


def idiom_guess(content):
    if content == '猜成语':
        guesser.startNewGuess()
        return True, idiom_hint

    if content == '查看更多':
        result = guesser.moreCandidate()
        return True, render_guess_result(result, False, guesser.lastCandidate)
    
    fields = re.split(r',|，', content)
    if len(fields) != 2:
        return False, '输入格式错误,' + idiom_hint

    guess_idiom, guess_result = fields[0].strip(), fields[1].strip()
    if len(guess_idiom) == 4 and guess_idiom in guesser.idiomMap:
        guess_idiom = guesser.idiomMap[guess_idiom]

    if len(guess_idiom.split()) != 4 or len(guess_result.split()) != 4:
        return False, '输入格式错误,' + idiom_hint

    result = guesser.guess(guess_idiom, guess_result)
    return True, render_guess_result(result, True, guesser.lastCandidate)


robot_userid = '_user_1'
def reply(content):
    at_user = ''
    if content.startswith('@' + robot_userid):
        at_user = robot_userid
        content = content[len(robot_userid)+2:]

    content = content.strip()
    if content == '猜成语':
        guesser.startNewGuess()
        return idiom_hint

    if guesser.isGuessing():
        match, result = idiom_guess(content)
        if match:
            return result
        else:
            return '当前还在猜成语呢, ' + result


    if '小可爱' in content:
        return random.choice(['小可爱在努力学习','小可爱在摸鱼','小可爱在研究小机器人呢','小可爱不睡觉觉了']) 

    if '可爱' in content:
        return '我就是这么可爱嘻嘻嘻'

    if '囡囡' in content:
        return '叫囡囡干嘛？'

    if '小哥哥' in content:
        return '小哥哥咋这么厉害！'

    if ('想你' in content) or ('想小可爱'in content):
        return '快到小可爱身边来！'
    
    if ('笨' in content) or  ('傻' in content):
        return '你才是大笨蛋'

    if '是' in content:
        return '可不是嘛'

    if '不' in content:
        return '没错，就是这样'

    return robot.answer(content) 

@event_manager.register("im.message.receive_v1")
def message_receive_event_handler(req_data: MessageReceiveEvent):
    sender_id = req_data.event.sender.sender_id
    message = req_data.event.message
    if message.message_type != "text":
        logging.warn("Other types of messages have not been processed yet")
        return jsonify()
        # get open_id and text_content
    open_id = sender_id.open_id
    chat_id = message.chat_id
    print(message.content, message.chat_id, message.chat_type)
	
    content = json.loads(message.content)['text']
    result = reply(content)
    # result = robot.answer(content)
    text_content = '{"text": "' + result + '"}' 
    # echo text message
    if message.chat_type == 'group':
        message_api_client.reply_text_message(message.message_id, text_content )
    else:    
        message_api_client.send_text_with_open_id(open_id, text_content)
    return jsonify()


@app.errorhandler
def msg_error_handler(ex):
    logging.error(ex)
    response = jsonify(message=str(ex))
    response.status_code = (
        ex.response.status_code if isinstance(ex, requests.HTTPError) else 500
    )
    return response


@app.route("/", methods=["POST"])
def callback_event_handler():
    # init callback instance and handle
    event_handler, event = event_manager.get_handler_with_event(VERIFICATION_TOKEN, ENCRYPT_KEY)

    return event_handler(event)


if __name__ == "__main__":
    # init()
    # print(reply('@_user_1 猜成语'))
    # print(reply('@_user_1 qiao3 duo2 tian1 gong1, 331 133 331 331'))
    app.run(host="0.0.0.0", port=3000, debug=True)
