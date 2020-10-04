import logging
import json
import os

from airflow.models import Connection
from airflow.utils.db import provide_session

logger = logging.getLogger(__name__)


@provide_session
def update_redis_db(params, session=None):
    db = (
        session
        .query(Connection)
        .filter(Connection.conn_id == 'redis_default')
        .first()
    )
    
    db.host = params['host']
    session.add(db)
    session.commit()


@provide_session
def update_postgres_db(params, session=None):
    db = (
        session
        .query(Connection)
        .filter(Connection.conn_id == 'postgres_default')
        .first()
    )

    db.host = params['host']
    db.login = params['login']
    db.set_password(params['password'])

    session.add(db)
    session.commit()


@provide_session
def update_airflow_db(params, session=None):
    db = (
        session
        .query(Connection)
        .filter(Connection.conn_id == 'airflow_db')
        .first()
    )

    db.conn_type = params['conn_type']
    db.host = params['host']
    db.login = params['login']
    db.set_password(params['password'])

    session.add(db)
    session.commit()


@provide_session
def update_azure_aci(params, session=None):
    db = (
        session
        .query(Connection)
        .filter(Connection.conn_id == 'azure_container_instances_default')
        .first()
    )

    db.conn_type = params['conn_type']
    db.login = params['login']
    db.set_password(params['password'])
    db.extra = json.dumps({
        "tenantId": params['tenantId'],
        "subscriptionId": params['subscriptionId']
    })

    session.add(db)
    session.commit()


@provide_session
def add_azure_registry(params, session=None):
    db = Connection(**params)

    session.add(db)
    session.commit()


if __name__ == "__main__":

    db_path = os.path.join(os.environ['AIRFLOW_HOME'],
                           'scripts', 'config', 'connections.json')

    with open(db_path, 'r') as f:
        db_config = json.load(f)

    logger.info('Updating db connections...')

    update_redis_db(db_config['redis_default'])
    update_postgres_db(db_config['postgres_default'])
    update_airflow_db(db_config['airflow_db'])
    update_azure_aci(db_config['azure_container_instances_default'])
    add_azure_registry(db_config['azure_registry_default'])
