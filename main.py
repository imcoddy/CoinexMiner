import CoinexAPI
import logging
import math
import time
import json


_private_api = CoinexAPI.PrivateAPI()


records = {}
records['bch_fees'] = 0
records['cdy_fees'] = 0
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
	data = _private_api.get_latest_transaction('CDYBCH')
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
				records['bch_fees'] = records['bch_fees'] + float(data['deal_fee'])
			else:
				records['cdy_fees'] = records['cdy_fees'] + float(data['deal_fee'])

			logging.info(records)
			return 'done'
		else:
			time.sleep(0.1)
			data = _private_api.get_order('CDYBCH',_id)
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
		data = _private_api.get_ticker('CDYBCH')
		data = data['data']
		sell_price = float(data['ticker']['sell'])
		buy_price = float(data['ticker']['buy'])
		delta = sell_price - buy_price
		if sell_price - buy_price >= 0.000000019:
			logging.info('space is enough')
			price = sell_price - 0.00000001
			amount = records['cdy_available'] / 10.0
			logging.info('sell %0.3f at %0.8f CDYBCH' % (amount,price))
			data_s = _private_api.sell(amount,price,'CDYBCH')
			logging.info('buy %0.3f at %0.8f CDYBCH' % (amount,price))
			data_b = _private_api.buy(amount,price,'CDYBCH')

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

	records['cdy_available'] = float(data['CDY']['available'])
	records['cet_available'] = float(data['CET']['available'])
	records['bch_available'] = float(data['BCH']['available'])

	logging.info('cdy_available: %0.3f' % records['cdy_available'])
	logging.info('cet_available: %0.3f' % records['cet_available'])
	logging.info('bch_available: %0.3f' % records['bch_available'])

def balance_cost():
	logging.info('need buy bch: %0.3f' % records['bch_fees'])
	data = _private_api.get_ticker('CETBCH')
	data = data['data']
	price = float(data['ticker']['sell'])
	amount = records[bch_fees] / price
	logging.info('sell %0.3f at %f CETBCH' % (amount,price))
	_private_api.sell(amount,price,'CETBCH')
	records[bch_fees] = 0
	
	
	logging.info('need buy cdy: %0.3f' % records['cdy_fees'])
	data = _private_api.get_ticker('CDYBCH')
	data = data['data']
	price = float(data['ticker']['buy'])
	amount = records[cdy_fees]
	logging.info('sell %0.3f at %f CDYBCH' % (amount,price))
	_private_api.buy(amount,price,'CDYBCH')
	records[cdy_fees] = 0

	logging.info(records)

def main():
	init_logger()
	logging.info('Start Mining!')

	while True:

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

		if records['variance'] < 0.7:
			logging.info('no fluctuation')
			
			status = digging()

		time.sleep(3)


		

if __name__ == "__main__":
	main()