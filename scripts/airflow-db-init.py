import logging

from airflow.configuration import conf
from airflow.models import Connection
from airflow.models.crypto import get_fernet
from airflow.utils.db import provide_session

logger = logging.getLogger(__name__)


@provide_session
def update_redis_db(key, session=None):
    db = (
            session
            .query(Connection)
            .filter(Connection.conn_id == 'redis_default')
            .first()
    )
    
    db.host = 'redis-kv'
    db.is_encrypted = False
    db.is_extra_encrypted = False
    session.add(db)
    session.commit()


@provide_session
def update_postgres_db(key, session=None):
    db = (
        session
        .query(Connection)
        .filter(Connection.conn_id == 'postgres_default')
        .first()
    )

    db.host = 'postgres-db'
    db.login = 'sa'
    db._password = key.encrypt(bytes('pwd', 'utf-8')).decode()

    session.add(db)
    session.commit()


@provide_session
def update_airflow_db(key, session=None):
    db = (
        session
        .query(Connection)
        .filter(Connection.conn_id == 'airflow_db')
        .first()
    )

    db.conn_type = 'postgres'
    db.host = 'postgres-db'
    db.login = 'sa'
    db._password = key.encrypt(bytes('pwd', 'utf-8')).decode()

    session.add(db)
    session.commit()


if __name__ == "__main__":
    # TODO: Read settings from YAML.

    logger.debug(f'Encrypting with {conf.get("core", "FERNET_KEY")}...')

    key = get_fernet()

    logger.info('Updating db connections...')

    update_redis_db(key)
    update_postgres_db(key)
    update_airflow_db(key)
