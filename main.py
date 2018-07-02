import CoinexAPI
import logging
import math
import time

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


def main():
	init_logger()
	logging.info('Start Mining!')

	_private_api = CoinexAPI.PrivateAPI()

	_variance = calculate_variance(_private_api) 

	if _variance < 0.5:
		logging.info('no fluctuation. wave ratio: %0.3f%%' % _variance)



	#data = _private_api.get_balances()

	#print(data)

	#data = _private_api.get_difficulty()

	#print(data)





	
		

if __name__ == "__main__":
	main()