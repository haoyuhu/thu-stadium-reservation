from utils.UrlBuilder import UrlBuilder
from utils.Common import Common
import requests
import collections
import urllib
import json


class RemoteService(object):
    SCHEMA = UrlBuilder.SCHEMA_HTTPS
    HOST = 'thu.stadium.huhaoyu.com'
    STADIUM_SEGMENTS = ['stadium']
    LIST_SEGMENTS = ['task', 'list']
    MAIL_SEGMENTS = ['task', 'notify']

    def __init__(self, secret_id, secret_key):
        super(RemoteService, self).__init__()
        self.secret_id = secret_id
        self.secret_key = secret_key

    def get_stadiums(self):
        url = UrlBuilder().schema(self.SCHEMA).host(self.HOST).segments(self.STADIUM_SEGMENTS).build()
        if url:
            params = self.__create_query_params_with_token()
            response = requests.get(url=url, params=params)
            return self.__get_data_from_response(response)
        return False

    def get_reservation_list(self):
        url = UrlBuilder().schema(self.SCHEMA).host(self.HOST).segments(self.LIST_SEGMENTS).build()
        if url:
            params = self.__create_query_params_with_token()
            response = requests.get(url=url, params=params)
            encrypted = self.__get_data_from_response(response)
            # delete useless '\0' which added by aes decryption
            if encrypted:
                json_string = Common.decrypt_content_by_aes(encrypted, self.secret_key)
                for i in xrange(len(json_string) - 1, 0, -1):
                    if json_string[i] == '}' or json_string[i] == ']':
                        json_string = json_string[:i + 1]
                        break
                return json.loads(json_string)
        return False

    def send_mail(self, open_id, group_id, record_list):
        json_string = json.dumps(record_list)
        encrypted = Common.encrypt_content_by_aes(json_string, self.secret_key)
        params = {
            'open_id': open_id,
            'group_id': group_id,
            'encrypted': encrypted
        }
        params = self.__create_query_params_with_token(params)
        params = self.__add_signature_to_query_params(params)

        url = UrlBuilder().schema(self.SCHEMA).host(self.HOST).segments(self.MAIL_SEGMENTS).build()
        if url:
            response = requests.post(url, data=params)
            if response.ok:
                json_obj = response.json()
                return json_obj and json_obj.get('error_code') == 0
        return False

    def __create_query_params_with_token(self, params=None):
        """
        :type params: dict
        """
        if params is None:
            params = {}
        params['secret_id'] = self.secret_id
        return params

    @staticmethod
    def __add_signature_to_query_params(params):
        """
        :type params: dict
        """
        op = collections.OrderedDict(sorted(params.items(), key=lambda t: t[0]))
        queries = urllib.urlencode(op)
        params['signature'] = Common.md5(queries)
        return params

    @staticmethod
    def __get_data_from_response(response):
        if not response.ok:
            return False
        json_obj = response.json()
        if json_obj.get('error_code') != 0:
            return False
        data = json_obj.get('data')
        return data if data is not None else False
