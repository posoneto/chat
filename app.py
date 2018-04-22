#!/usr/bin/env python3

import pip
pip.main(['install', 'requests'])
pip.main(['install', 'scipy'])

import requests
from requests.compat import urljoin
import json

from dialogue_manager import DialogueManager
from utils import RESOURCE_PATH

import sys
import warnings

import socket
import threading

if not sys.warnoptions:
    warnings.simplefilter("ignore")


class BotHandler(object):

    def __init__(self, dialogue_manager):
        self.dialogue_manager = dialogue_manager

    def get_answer(self, question):
        if question == '/start':
            return "Hi, I am your project bot. How can I help you today?"
        return self.dialogue_manager.generate_answer(question)


def main():

    dialogue_manager = DialogueManager(RESOURCE_PATH)

    bot = BotHandler(dialogue_manager)

    print('\nCreating and Training Chatbot, this will take about 4 minutes, please wait...\n')
    dialogue_manager.create_chitchat_bot()
    print("Ready to talk!")

    host = '' #socket.gethostname() # Get local machine name # "http://chat-chat.1d35.starter-us-east-1.openshiftapps.com"
    port = 4040

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind((host, port))
    sock.listen(1)

    print('host: ', host)

    def before(value, a):
        # Find first part and return slice before it.
        pos_a = value.find(a)
        if pos_a == -1:
            return ""
        return value[0:pos_a]

    def after(value, a):
        # Find and validate first part.
        pos_a = value.rfind(a)
        if pos_a == -1:
            return ""
        # Returns chars after the found string.
        adjusted_pos_a = pos_a + len(a)
        if adjusted_pos_a >= len(value):
            return ""
        return value[adjusted_pos_a:]

    def parse_data(data):
        # old version (brute force):
        # question = before(after(data, '"text":"'), '"')
        # from_id = before(after(data, '"recipient":{"id":"'), '"')
        # conversation_id = before(after(data, '"conversation":{"id":"'), '"')
        # recipient_id = before(after(data, '"from":{"id":"'), '"')
        # reply_to_id = before(after(data, ',"id":"'), '"')

        # question = data['text']
        # from_id = data['recipient']['id']
        # conversation_id = data['conversation']['id']
        # recipient_id = data['from']['id']
        # reply_to_id = data['id']

        question = data.get('text', '')
        from_id = data.get('recipient', {}).get('id', '')
        conversation_id = data.get('conversation', {}).get('id', '')
        recipient_id = data.get('from', {}).get('id', '')
        reply_to_id = data.get('id', '')

        return question, from_id, conversation_id, recipient_id, reply_to_id

    def handler(c, a, bot):
        while True:
            try:
                data = c.recv(1024)
                if data:
                    data_str = str(data, 'utf-8')

                    (request_header, request_body) = data_str.split("\r\n\r\n")
                    request_body = json.loads(request_body)
                    request_type = request_body.get('type', '')

                    if request_type == 'message':
                        question, from_id, conversation_id, recipient_id, reply_to_id = parse_data(
                            request_body)
                        text = bot.get_answer(question)

                        if text == '':
                            text = "Hmm, you are sending some weird characters to me..."

                        print('\nquestion:', question, '\nanswer:', text)

                        body = {'type': 'message', 'from': {'id': from_id, 'name': 'Walter bot'},
                                'conversation': {'id': conversation_id, 'name': 'Walter conversation'},
                                'recipient': {'id': recipient_id, 'name': 'Walter user'},
                                'text': text, 'replyToId': reply_to_id}

                        body_json = json.dumps(body)

                        # c.send(bytes(text, "utf8"))

                        base_url = request_body.get('serviceUrl', '')
                        try:
                            api_url = urljoin(
                                base_url, '/v3/conversations/' + conversation_id + '/activities/' + reply_to_id)
                            requests.post(api_url, data=body_json, headers={
                                          'Content-Type': 'application/json'})
                            # c.send(bytes('HTTP/1.1 200 OK', 'utf-8'))
                            # print('sending body...', bytes(body_json, 'utf-8'))
                            # c.send(bytes(body_json, 'utf-8'))
                            # finally:
                            #     pass
                        except:
                            print('something wrong with the post!')

                else:
                    # print('no data')
                    break

            except:
                break

        c.close()

    while True:
        c, a = sock.accept()
        cThread = threading.Thread(target=handler, args=(c, a, bot))
        cThread.daemon = True
        cThread.start()
        print('connection: ', c)
        print('argument: ', a)


if __name__ == "__main__":
    main()
