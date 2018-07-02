import CoinexAPI
import logging
import math
import time
import json
import pickle


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



def balance_cost():
	logging.info('need buy bch: %0.3f' % records['bch_fees'])
	data = _private_api.get_ticker('CETBCH')
	data = data['data']
	price = float(data['ticker']['buy'])
	amount = records['bch_fees'] / price
	logging.info('sell %0.3f at %f CETBCH' % (amount,price))
	_private_api.sell(amount,price,'CETBCH')
	records['bch_fees'] = 0
	
	
	logging.info('need buy cdy: %0.3f' % records['cdy_fees'])
	data = _private_api.get_ticker('CDYBCH')
	data = data['data']
	price = float(data['ticker']['sell'])
	amount = records['cdy_fees']
	logging.info('buy %0.3f at %f CDYBCH' % (amount,price))
	_private_api.buy(amount,price,'CDYBCH')
	records['cdy_fees'] = 0

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

	if records['bch_fees'] == 0 or records['cdy_fees'] == 0:
		logging.info('no need to balance the cost')
		return


	logging.info(records)
	balance_cost()
	records['balance_cost_time'] = time.time()
	pickle.dump(records,open('cache.data','wb'))


		

if __name__ == "__main__":
	main()