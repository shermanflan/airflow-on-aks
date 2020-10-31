import logging

from cryptography.fernet import Fernet
import redis

logging.basicConfig(
    format='%(asctime)s %(levelname)s [%(name)s]: %(message)s'
    , datefmt='%Y-%m-%d %I:%M:%S %p'
    , level=logging.DEBUG)

logger = logging.getLogger(__name__)


def run(coins, C):
    memo = [
        [n for n in range(C+1)]
        for _ in coins
    ]

    for i_coin, coin in enumerate(coins[1:], start=1):
        for coin_sum in range(C+1):
            if coin <= coin_sum:
                memo[i_coin][coin_sum] = min(memo[i_coin][coin_sum - coin] + 1,
                                             memo[i_coin-1][coin_sum])
            else:
                memo[i_coin][coin_sum] = memo[i_coin-1][coin_sum]
    return memo[-1][-1]


if __name__ == '__main__':

    logger.info('Generate fernet key')
    # fernet_key = Fernet.generate_key()
    # logger.info(f'Fernet: {fernet_key.decode()}')

    logger.info('Connect to redis')
    # r = redis.Redis(host='40.76.155.221', port=6379, db=0)
    # r.set('rko', '21')
    # logger.info(f"RESULT: {r.get('foo')}")

    logger.info(run([1, 5, 6, 8], 21))