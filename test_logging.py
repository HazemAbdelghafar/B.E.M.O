import logging

x = 1

logger = logging.getLogger(__name__)
logging.basicConfig(format='%(asctime)s %(filename)s %(levelname)s: %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p', filename='./logging.log', encoding='utf-8', level=logging.DEBUG)


console_handler = logging.StreamHandler()
logger.addHandler(console_handler)

logger.info(f'So should this {x}')
logger.error('And non-ASCII stuff, too, like Øresund and Malmö')
logger.info("*" * 20)
