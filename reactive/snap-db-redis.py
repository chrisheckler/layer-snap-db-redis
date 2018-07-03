from charms.reactive import (
    when,
    when_not,
    set_flag,
    endpoint_from_flag,
)

from charmhelpers.core.hookenv import status_set, log

from charmhelpers.core import unitdata


REDIS_OUT = '/home/ubunutu/redis_config.txt'
PGSQL_OUT = '/home/ubuntu/postgreSQL_config.txt'
KV = unitdata.kv()


@when_not('snap.flask-gunicorn-nginx.installed')
def snap_installed():
    """ Snap installed 
    """

    status_set('active', 'Snap flask-gunicorn-nginx installed')
    log('Snap Installed')
    set_flag('snap.flask-gunicorn-nginx.installed')
    

@when('pgsql.connected')
@when_not('snap-db-redis.pgsql.requested')
def request_database():
    """ Requesting snap-db-redis pgsql
    """

    status_set('maintenance', 'Requesting PostgreSQL database')
    pgsql = endpoint_from_flag('pgsql.connected')
    pgsql.set_database('snap-db-redis')
    
    log('Database Available')
    status_set('active','pgsql.requested')
    set_flag('snap-db-redis.pgsql.requested')


@when('pgsql.master.available',
      'snap-db-redis.pgsql.requested')
@when_not('snap-db-redis.pgsql.available')
def save_database_connection_info():
    """ Saves the config data to unitdata
    """ 

    status_set('maintenance', 
               'Getting/Setting snap-db-redis config data')

    pgsql = endpoint_from_flag('pgsql.master.available')
   
    KV.set('dbname', pgsql.master.dbname)
    KV.set('dbuser', pgsql.master.user)
    KV.set('dbpass', pgsql.master.password)
    KV.set('dbhost', pgsql.master.host)
    KV.set('dbport', pgsql.master.port)

    status_set('active', 'Snap-db-redis database available')
    set_flag('snap-db-redis.pgsql.available')
    log('Snap-db-redis Database Available')


@when('snap-db-redis.pgsql.available')
@when_not('snap-db-redis.config.available')
def output_database_config():
    """ Outputting config to snap-db-redis HOME dir for now.
    """

    status_set('maintenance', 'Writing config')
    db_config = KV.getrange('db')

    pgsql_config = \
        'postgresql://{dbuser}:{dbpass}@{dbhost}:{dbport}/{dbname}\n'.format(**db_config)

    with open(PGSQL_OUT, 'a') as f:
        f.write(pgsql_config)
    
    log('PostgreSQL available')
    status_set('active', 'Snap-db-redis postgreSQL config available')
    set_flag('snap-db-redis.config.available')


@when('endpoint.redis.available')
@when_not('endpoint.redis.configured')
def get_redis_data(redis):
    """ Get redis data
    """

    status_set('maintenance', 'Getting data')

    for app in endpoint_from_flag(
        'endpoint.redis.available').relation_data():
        for redis_node in application['hosts']:
            KV.set('redis_data_host', redis_node['hosts'])
            KV.set('redis_data_port', int(redis_node['port']))
            KV.set('redis_data_db', 0)
    
    redis_data = endpoint_from_flag('endpoint.redis.available').relation_data()
    with open(REDIS_OUT, 'a') as f:
        f.write(str(redis_data.getitems()))

    status_set('active', 'Redis Configured')
    log('Redis Data Configured')
    set_flag('endpoint.redis.configured')    
    












