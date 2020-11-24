import logging
import os

from cryptography.fernet import Fernet
import redis

log_level_code = getattr(logging, os.environ.get('LOG_LEVEL', ''), logging.INFO)
logging.basicConfig(
    format='%(asctime)s %(levelname)s [%(name)s]: %(message)s'
    , datefmt='%Y-%m-%d %I:%M:%S %p'
    , level=log_level_code)

logger = logging.getLogger(__name__)

def countBits(num):
    result, i = [0], 1

    while i <= num:

        if (num - 1) & 1 == 0:  # even
            result.append(result[i - 1] + 1)
        else:
            if i & (i - 1) == 0:  # power of 2
                result.append(1)
            else:
                result.append(result[i - 1])
        i += 1

    return result


if __name__ == '__main__':

    logger.info('Generate fernet key')
    # fernet_key = Fernet.generate_key()
    # logger.info(f'Fernet: {fernet_key.decode()}')

    logger.info('Connect to redis')
    # r = redis.Redis(host='40.76.155.221', port=6379, db=0)
    # r.set('rko', '21')
    # logger.info(f"RESULT: {r.get('foo')}")

    countBits(5)