# Copyright (C) 2013, Maxime Biais <maxime@biais.org>

import config
import time
import hashlib
import json as complex_json
import requests
import logging
import time

class RequestClient(object):
    __headers = {
        'Content-Type': 'application/json; charset=utf-8',
        'Accept': 'application/json',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.90 Safari/537.36'
    }

    def __init__(self, headers={}):
        self.access_id = config.coinex_api_id
        self.secret_key = config.coinex_api_key
        self.headers = self.__headers
        self.headers.update(headers)

    @staticmethod
    def get_sign(params, secret_key):
        sort_params = sorted(params)
        data = []
        for item in sort_params:
            data.append(item + '=' + str(params[item]))
        str_params = "{0}&secret_key={1}".format('&'.join(data), secret_key)
        token = hashlib.md5(str.encode(str_params)).hexdigest().upper()
        return token

    def set_authorization(self, params):
        params['access_id'] = self.access_id
        params['tonce'] = int(time.time()*1000)
        self.headers['AUTHORIZATION'] = self.get_sign(params, self.secret_key)

    def _request(self, method, url, params={}, data='', json={}):
        method = method.upper()
        if method == 'GET':
            self.set_authorization(params)
            result = requests.request('GET', url, params=params, headers=self.headers)
        else:
            if data:
                json.update(complex_json.loads(data))
            self.set_authorization(json)
            result = requests.request(method, url, json=json, headers=self.headers)
        return result

    def request(self, method, url, params={}, data='', json={}):
        try:
            return self._request(method,url,params,data,json)
        except Exception as e:
            logging.error(e)
            time.sleep(0.5)
            return self._request(method,url,params,data,json)
  




class PrivateAPI(object):

    def __init__(self):
        super().__init__()
    
        

    def buy(self, amount, price, market):
        """Create a buy limit order"""
        request_client = RequestClient()

        data = {
                "amount": "%.8f" % (amount),
                "price": "%.8f" % (price),
                "type": "buy",
                "market": market
            }

        response = request_client.request(
                'POST',
                'https://api.coinex.com/v1/order/limit',
                json=data,
        )

        if response != None:
            data = complex_json.loads(response.text)
            if data["code"] != 0:
                raise Exception(data["message"])
            elif "data" in data:         
                return data


    def sell(self, amount, price, market):
        """Create a sell limit order"""
        request_client = RequestClient()

        data = {
                "amount": "%.8f" % (amount),
                "price": "%.8f" % (price),
                "type": "sell",
                "market": market
            }

        response = request_client.request(
                'POST',
                'https://api.coinex.com/v1/order/limit',
                json=data,
        )

        if response != None:
            data = complex_json.loads(response.text)
            if data["code"] != 0:
                raise Exception(data["message"])
            elif "data" in data:         
                return data

    def get_balances(self):
        """Get balance"""
        request_client = RequestClient()
        response = request_client.request('GET', 'https://api.coinex.com/v1/balance/')

        if response != None:
            data = complex_json.loads(response.text)
            if data["code"] != 0:
                raise Exception(data["message"])
            elif "data" in data:         
                return data
        else:
            raise Exception("Critical error no get_balances")


    def get_difficulty(self):
        """Get Difficulty"""
        request_client = RequestClient()
        response = request_client.request('GET', 'https://api.coinex.com/v1/order/mining/difficulty')

        if response != None:
            data = complex_json.loads(response.text)
            if data["code"] != 0:
                raise Exception(data["message"])
            elif "data" in data:         
                return data
        else:
            raise Exception("Critical error no get_difficulty")
     

    def get_latest_transaction(self,market):
        request_client = RequestClient()
        response = request_client.request('GET', 'https://api.coinex.com/v1/market/deals?market='+market)

        if response != None:
            data = complex_json.loads(response.text)
            if data["code"] != 0:
                raise Exception(data["message"])
            elif "data" in data:         
                return data
        else:
            raise Exception("Critical error no get_latest_transaction")

    def get_ticker(self,market):
        request_client = RequestClient()
        response = request_client.request('GET', 'https://api.coinex.com/v1/market/ticker?market='+market)

        if response != None:
            data = complex_json.loads(response.text)
            if data["code"] != 0:
                raise Exception(data["message"])
            elif "data" in data:         
                return data
        else:
            raise Exception("Critical error no get_ticker")

    def get_orders(self,market):
        request_client = RequestClient()

        data = {
                "page": 1,
                "limit": 100,
                "market": market
            }

        response = request_client.request(
                'GET',
                'https://api.coinex.com/v1/order/pending',
                params=data,
        )

        if response != None:
            data = complex_json.loads(response.text)
            if data["code"] != 0:
                raise Exception(data["message"])
            elif "data" in data:         
                return data
        else:
            raise Exception("Critical error no get_orders")

    def get_order(self,market,_id):
        request_client = RequestClient()

        data = {
                "id": _id,
                "market": market
            }

        response = request_client.request(
                'GET',
                'https://api.coinex.com/v1/order',
                params=data,
        )

        if response != None:
            data = complex_json.loads(response.text)
            if data["code"] != 0:
                raise Exception(data["message"])
            elif "data" in data:         
                return data
        else:
            raise Exception("Critical error no get_order")



