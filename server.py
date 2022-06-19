#!/usr/bin/env python3.8

import json
import logging
import requests
from api import MessageApiClient, VERIFICATION_TOKEN, ENCRYPT_KEY
from event import MessageReceiveEvent, UrlVerificationEvent, EventManager
from flask import Flask, jsonify
import threading

import chat_module

app = Flask(__name__)

# init service
message_api_client = MessageApiClient()
event_manager = EventManager()

@event_manager.register("url_verification")
def request_url_verify_handler(req_data: UrlVerificationEvent):
    # url verification, just need return challenge
    if req_data.event.token != VERIFICATION_TOKEN:
        raise Exception("VERIFICATION_TOKEN is invalid")
    return jsonify({"challenge": req_data.event.challenge})


robot_userid = '_user_1'
def reply(content):
    at_user = ''
    if content.startswith('@' + robot_userid):
        at_user = robot_userid
        content = content[len(robot_userid)+2:]

    content = content.strip()

    for m in chat_module.Modules:
        try:
            c = m.Handle(content)
            if c is not None:
                return c
        except Exception as e:
            print(e)
            return f'Exception: {e}'

    return '没有回答了'

def processReceiveEvent(req_data: MessageReceiveEvent):
    sender_id = req_data.event.sender.sender_id
    message = req_data.event.message
    open_id = sender_id.open_id
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

@event_manager.register("im.message.receive_v1")
def message_receive_event_handler(req_data: MessageReceiveEvent):
    message = req_data.event.message
    if message.message_type != "text":
        logging.warn("Other types of messages have not been processed yet")
        return jsonify()

    thr = threading.Thread(target=processReceiveEvent, args=req_data)
    thr.start()
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
    app.run(host="0.0.0.0", port=3000, debug=True)
