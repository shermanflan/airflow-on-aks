import logging

from airflow.models import Connection
from airflow.utils.db import provide_session

logger = logging.getLogger(__name__)


@provide_session
def update_redis_db(session=None):
    db = (
            session
            .query(Connection)
            .filter(Connection.conn_id == 'redis_default')
            .first()
    )
    
    db.host = 'redis-kv'
    session.add(db)
    session.commit()

if __name__ == "__main__":

    # Update redis connection.
    update_redis_db()

    logger.info('Updated redis connection...')