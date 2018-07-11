import CoinexAPI
import logging
import math
import time
import json
import pickle
import config
import os


_private_api = CoinexAPI.PrivateAPI()


records = {}


def init_logger():
    logging.VERBOSE = 15
    logging.verbose = lambda x: logging.log(logging.VERBOSE, x)
    logging.addLevelName(logging.VERBOSE, "VERBOSE")

    level = logging.INFO
 
    logging.basicConfig(format='%(asctime)s [%(levelname)s] %(message)s',
                        level=level)

    fh = logging.FileHandler('./log.txt')
    formatter = logging.Formatter('%(asctime)s [%(levelname)s] %(message)s')
    fh.setFormatter(formatter)
    logging.getLogger('').addHandler(fh)


def balance_cost():
	if records['money_fees'] < 0.001 or records['goods_fees'] < 10.0 :
		logging.info('no need to balance the cost')
		return

	money_markets = 'CET' + config.money
	logging.info('need buy %s: %0.3f' % (records['money_fees'],config.money))
	data = _private_api.get_ticker(money_markets)
	data = data['data']
	price = float(data['ticker']['buy'])
	amount = records['money_fees'] / price
	logging.info('sell %0.3f at %f %s' % (amount,price,money_markets))
	_private_api.sell(amount,price,money_markets)
	records['money_fees'] = 0
	
	goods_markets = config.market
	logging.info('need buy %s: %0.3f' % (records['goods_fees'],config.goods))
	data = _private_api.get_ticker(goods_markets)
	data = data['data']
	price = float(data['ticker']['sell'])
	amount = records['goods_fees']
	logging.info('buy %0.3f at %f %s' % (amount,price,goods_markets))
	_private_api.buy(amount,price,goods_markets)
	records['goods_fees'] = 0

	logging.info(records)

def main():
	global records

	init_logger()
	logging.info('Start balance cost!')

	try:
		records = pickle.load(open('cache.data','rb'))
	except Exception as e:
		logging.info('no cache file found.')
		return


	logging.info(records)
	balance_cost()
	records['balance_cost_time'] = time.time()
	pickle.dump(records,open('cache.data','wb'))


		

if __name__ == "__main__":
	main()
	os.system("pause")