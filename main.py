import logging

from cryptography.fernet import Fernet
import redis

logging.basicConfig(
    format='%(asctime)s %(levelname)s [%(name)s]: %(message)s'
    , datefmt='%Y-%m-%d %I:%M:%S %p'
    , level=logging.DEBUG)

logger = logging.getLogger(__name__)


def run(nums, target):

    start, mid, end = 0, (len(nums)-1)//2, len(nums)-1

    while start <= end:

        mid = (end-start)//2 + start

        if nums[mid] == target:
            return mid

        if nums[start] <= nums[mid]:
            if target >= nums[start] and target < nums[mid]:
                end = mid - 1
            else:
                start = mid + 1
        else:
            if target > nums[mid] and target <= nums[end]:
                start = mid + 1
            else:
                end = mid - 1

    return -1


if __name__ == '__main__':

    logger.info('Generate fernet key')
    # fernet_key = Fernet.generate_key()
    # logger.info(f'Fernet: {fernet_key.decode()}')

    logger.info('Connect to redis')
    # r = redis.Redis(host='40.76.155.221', port=6379, db=0)
    # r.set('rko', '21')
    # logger.info(f"RESULT: {r.get('foo')}")

    logger.info(run([5,1,2,3,4], 1))