import logging

from cryptography.fernet import Fernet

logging.basicConfig(format='%(asctime)s %(levelname)s [%(name)s]: %(message)s',
                    datefmt='%Y-%m-%d %I:%M:%S %p', level=logging.DEBUG)

logger = logging.getLogger(__name__)

if __name__ == '__main__':

    logger.info('Generate fernet key...')

    fernet_key = Fernet.generate_key()
    logger.info(f'Fernet: {fernet_key.decode()}')
