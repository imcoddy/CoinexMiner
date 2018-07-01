import CoinexAPI
import logging

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


def main():
	init_logger()
	logging.info('Start Mining!')

	_private_api = CoinexAPI.PrivateAPI()

	data = _private_api.get_info()

	print(data)

		

if __name__ == "__main__":
	main()