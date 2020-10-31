import logging
import json
import os

from airflow.models import Connection, Variable
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
def add_azure_registry(params, session=None):
    db = Connection(**params)

    session.add(db)
    session.commit()


@provide_session
def update_aci_connection(params, session=None):
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
def add_aci_config(key, path, session=None):
    # TODO: Storing the full config as a variable is visible to
    # anyone who can see the Variables screen. This is insecure
    # so it would be preferable to use a key vault.
    with open(path, 'r') as f:
        config = json.load(f)
        Variable.set(key, value=config,
                     serialize_json=True, session=session)


@provide_session
def add_default_user(session=None):
    from airflow import models
    from airflow.contrib.auth.backends.password_auth import PasswordUser

    user = PasswordUser(models.User())
    user.username = 'shermanflan'
    user.email = 'shermanflan@gmail.com'
    user.password = 'pwd'
    user.superuser = True

    session.add(user)
    session.commit()


if __name__ == "__main__":

    db_path = os.path.join(os.environ['AIRFLOW_HOME'],
                           'scripts', 'metadata', 'connections.json')

    with open(db_path, 'r') as f:
        db_config = json.load(f)

    logger.info('Updating db connections...')

    update_redis_db(db_config['redis_default'])
    update_postgres_db(db_config['postgres_default'])
    update_airflow_db(db_config['airflow_db'])
    update_aci_connection(db_config['azure_container_instances_default'])
    add_azure_registry(db_config['azure_registry_default'])

    # if bool(os.environ.get('AIRFLOW__WEBSERVER__AUTHENTICATE', False)) \
    #         and not bool(os.environ.get('AIRFLOW__WEBSERVER__RBAC', False)):
    #     logger.info('Adding default user...')
    #     add_default_user()

    logger.info('Updating variables...')

    # TODO: Convert to configurable mapping.
    aci_path = os.path.join(os.environ['AIRFLOW_HOME'],
                            'scripts', 'config', 'box2lake.json')

    add_aci_config('aci_config', aci_path)