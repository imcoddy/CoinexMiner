import CoinexAPI
import logging
import math
import time
import json
import pickle
import config


_private_api = CoinexAPI.PrivateAPI()


records = {}
records['money_fees'] = 0
records['goods_fees'] = 0
records['balance_cost_time'] = time.time()
records['variance'] = 1

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


def calculate_variance(_private_api):
	data = _private_api.get_latest_transaction(config.market)
	data = data['data']
	_sum = 0
	for x in data:
		_sum = _sum + float(x['price'])

	_avg = _sum / float(len(data))

	_sum = 0

	for x in data:
		_price = float(x['price'])
		_sum = _sum + (_price - _avg)*( _price - _avg)

	_variance = math.sqrt(_sum / float(len(data)))
	_variance = _variance / _avg * 100

	return _variance


def check_order_state(_type,data):
	data = data['data']

	_id = data['id']

	index = 0

	left_amout = float(data['left'])

	while True:
		if left_amout == 0:
			if _type == 'sell':
				records['money_fees'] = records['money_fees'] + float(data['deal_fee'])
			else:
				records['goods_fees'] = records['goods_fees'] + float(data['deal_fee'])

			logging.info(records)
			return 'done'
		else:
			time.sleep(0.1)
			data = _private_api.get_order(config.market,_id)
			data = data['data']
			left_amout = float(data['left'])
			logging.info('check order state: id %d left %0.3f' % (_id,left_amout))

		index = index+1
		if index > 60*10:
			return 'timeout'
		time.sleep(1)



def digging():
	index = 0
	while True:
		data = _private_api.get_ticker(config.market)
		data = data['data']
		sell_price = float(data['ticker']['sell'])
		buy_price = float(data['ticker']['buy'])
		delta = sell_price - buy_price
		if sell_price - buy_price >= 0.000000019:
			logging.info('space is enough')
			price = sell_price - 0.00000001
			price_s = price
			price_b = price * (1 - config.bid_ask_spread/100.0)
			amount = records['goods_available'] * config.partial_ratio
			logging.info('sell %0.3f at %0.8f %s' % (amount,price_s,config.market))
			data_s = _private_api.sell(amount,price,config.market)
			logging.info('buy %0.3f at %0.8f %s' % (amount,price_b,config.market))
			data_b = _private_api.buy(amount,price,config.market)

			stats_b = check_order_state('buy',data_b)
			stats_s = check_order_state('sell',data_s)

			if stats_b == 'timeout' or stats_s == 'timeout':
				logging.info('wait order too much time')
				return 'timeout'

		index = index+1
		if index > 20:
			return 'maximum'
		time.sleep(0.05)

def need_pause():
	data = ''
	try:
		data = _private_api.get_difficulty()
	except Exception as e:
		logging.info('need_pause failed try again 1')
		time.sleep(10)
		try:
			data = _private_api.get_difficulty()
		except Exception as e:
			logging.info('need_pause failed try again 2')
			time.sleep(5*60)
			data = _private_api.get_difficulty()
	
	data = data['data']

	difficulty = float(data['difficulty'])
	prediction = float(data['prediction'])
	if prediction > difficulty * 0.95:
		logging.info('difficulty %f prediction %f' % (difficulty,prediction))
		return True
	else:
		return False

def update_balance():
	data = _private_api.get_balances();
	data = data['data']

	records['goods_available'] = float(data[config.goods]['available'])
	records['cet_available'] = float(data['CET']['available'])
	records['money_available'] = float(data[config.money]['available'])

	logging.info('goods_available: %0.3f' % records['goods_available'])
	logging.info('cet_available: %0.3f' % records['cet_available'])
	logging.info('money_available: %0.3f' % records['money_available'])

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
	logging.info('Start Mining!')

	try:
		records = pickle.load(open('cache.data','rb'))
		logging.info(records)
	except Exception as e:
		logging.info('no cache file found.')


	while True:

		try:
			update_balance()
		except Exception as e:
			logging.info('update_balance failed try again 1')
			time.sleep(10)
			try:
				update_balance()
			except Exception as e:
				logging.info('update_balance failed try again 2')
				time.sleep(5*60)				
				update_balance()


			

		cur_time = time.time()

		if cur_time - records['balance_cost_time'] > 60*60:
			logging.info('balance the fee cost')
			balance_cost()
			records['balance_cost_time'] = cur_time

		if need_pause():
			logging.info('need_pause mine too much')
			time.sleep(5)
			continue

		try:
			records['variance'] = calculate_variance(_private_api)
		except json.decoder.JSONDecodeError as e:
			logging.error('calculate_variance json.decoder.JSONDecodeError')

		

		logging.info('wave ratio: %0.3f%%' % records['variance'])

		if records['variance'] < config.wave_ratio:
			logging.info('no fluctuation')
			
			status = digging()

		pickle.dump(records,open('cache.data','wb'))

		time.sleep(3)


		

if __name__ == "__main__":
	main()