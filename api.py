#! /usr/bin/env python3.8
import os
import logging
import requests
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

APP_ID = os.getenv("APP_ID")
APP_SECRET = os.getenv("APP_SECRET")
VERIFICATION_TOKEN = os.getenv("VERIFICATION_TOKEN")
ENCRYPT_KEY = os.getenv("ENCRYPT_KEY")
LARK_HOST = os.getenv("LARK_HOST")
MOIVE_DOC_URL = os.getenv("MOIVE_DOC_URL")
PODCAST_URL = os.getenv("PODCAST_URL")

# const
TENANT_ACCESS_TOKEN_URI = "/open-apis/auth/v3/tenant_access_token/internal"
MESSAGE_URI = "/open-apis/im/v1/messages"


class MessageApiClient(object):
    def __init__(self):
        self._app_id = APP_ID
        self._app_secret = APP_SECRET
        self._lark_host = LARK_HOST
        self._tenant_access_token = ""

    @property
    def tenant_access_token(self):
        return self._tenant_access_token

    def send_text_with_open_id(self, open_id, content):
        self.send("open_id", open_id, "text", content)

    def upload_image(self, image_path, image_type='message'):
        self._authorize_tenant_access_token()
        url = f'{self._lark_host}/open-apis/im/v1/images'
        headers = {
            #'Content-Type': 'multipart/form-data',
            "Authorization": "Bearer " + self.tenant_access_token,
        }
        #print(headers)

        _, image_name = os.path.split(image_path)
        
        payload={'image_type': image_type}
        files=[
          ('image',(image_name, open(image_path,'rb'),'image/jpeg'))
        ]
        resp = requests.post(url=url, headers=headers, files=files, data=payload)
        print(resp)
        MessageApiClient._check_error_response(resp)
        return resp.json()['data']['image_key']

    def upload_medias(self, media_url, parent_node='bascn8PCizNlokom09WfnN89O3b'):
        self._authorize_tenant_access_token()
        url = f'{self._lark_host}/open-apis/drive/v1/medias/upload_all'
        headers = {
            #'Content-Type': 'multipart/form-data',
            "Authorization": "Bearer " + self.tenant_access_token,
        }
        # print(headers)

        media_data = requests.get(media_url).content
        with open('/tmp/sample.jpg', 'wb') as fp:
            fp.write(media_data)
        files=[
          ('file',('sample.jpg', open('/tmp/sample.jpg','rb'),'image/jpeg'))
        ]
        size = str(len(media_data))
        payload={
            'file_name':'sample.jpg',
            'parent_type':'bitable_image',
            'parent_node': parent_node,
            'size': size,
        }
        resp = requests.post(url=url, headers=headers, files=files, data=payload)
        # print(resp.content)
        MessageApiClient._check_error_response(resp)
        return resp.json()['data']['file_token']


    def send(self, receive_id_type, receive_id, msg_type, content):
        # send message to user, implemented based on Feishu open api capability. doc link: https://open.feishu.cn/document/uAjLw4CM/ukTMukTMukTM/reference/im-v1/message/create
        self._authorize_tenant_access_token()
        url = "{}{}?receive_id_type={}".format(
            self._lark_host, MESSAGE_URI, receive_id_type
        )
        headers = {
            "Content-Type": "application/json",
            "Authorization": "Bearer " + self.tenant_access_token,
        }

        req_body = {
            "receive_id": receive_id,
            "content": content,
            "msg_type": msg_type,
        }
        resp = requests.post(url=url, headers=headers, json=req_body)
        MessageApiClient._check_error_response(resp)

    def reply_text_message(self, message_id, content):
        self._authorize_tenant_access_token()
        url = f"{self._lark_host}{MESSAGE_URI}/{message_id}/reply"

        headers = {
            "Content-Type": "application/json",
            "Authorization": "Bearer " + self.tenant_access_token,
        }

        req_body = {'msg_type': 'text', 'content': content}
        resp = requests.post(url=url, headers=headers, json=req_body)
        MessageApiClient._check_error_response(resp)


    def list_bittable_records(self, app_token, table_id):
        self._authorize_tenant_access_token()
        url = f'{self._lark_host}/open-apis/bitable/v1/apps/{app_token}/tables/{table_id}/records'
        headers = {
            "Content-Type": "application/json",
            "Authorization": "Bearer " + self.tenant_access_token,
        }
        resp = requests.get(url=url, headers=headers)
        MessageApiClient._check_error_response(resp)
        return resp.json()

    def new_bittable_records(self, app_token, table_id, content):
        self._authorize_tenant_access_token()
        url = f'{self._lark_host}/open-apis/bitable/v1/apps/{app_token}/tables/{table_id}/records'
        headers = {
            "Content-Type": "application/json",
            "Authorization": "Bearer " + self.tenant_access_token,
        }

        req_body = {"fields":content}
        print(self.tenant_access_token, req_body)
        
        resp = requests.post(url=url, headers=headers, json=req_body)
        MessageApiClient._check_error_response(resp)
        return resp.json()

    def _authorize_tenant_access_token(self):
        # get tenant_access_token and set, implemented based on Feishu open api capability. doc link: https://open.feishu.cn/document/ukTMukTMukTM/ukDNz4SO0MjL5QzM/auth-v3/auth/tenant_access_token_internal
        url = "{}{}".format(self._lark_host, TENANT_ACCESS_TOKEN_URI)
        req_body = {"app_id": self._app_id, "app_secret": self._app_secret}
        response = requests.post(url, req_body)
        MessageApiClient._check_error_response(response)
        self._tenant_access_token = response.json().get("tenant_access_token")

    @staticmethod
    def _check_error_response(resp):
        # check if the response contains error information
        if resp.status_code != 200:
            resp.raise_for_status()
        response_dict = resp.json()
        code = response_dict.get("code", -1)
        if code != 0:
            logging.error(response_dict)
            raise LarkException(code=code, msg=response_dict.get("msg"))


class LarkException(Exception):
    def __init__(self, code=0, msg=None):
        self.code = code
        self.msg = msg

    def __str__(self) -> str:
        return "{}:{}".format(self.code, self.msg)

    __repr__ = __str__
