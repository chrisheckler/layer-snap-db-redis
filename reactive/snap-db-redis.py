from charms.reactive import (
    when,
    when_not,
    set_flag,
    endpoint_from_flag,
)

from charmhelpers.core.hookenv import status_set, log

from charmhelpers.core import unitdata


REDIS_OUT = '/home/ubuntu/redis_config.txt'
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
        'postgresql://{dbuser}:{dbpass}@{dbhost}:{dbport}/{dbname}'.format(**db_config)

    with open(PGSQL_OUT, 'a') as f:
        f.write(pgsql_config)
    
    log('PostgreSQL available')
    status_set('active', pgsql_config)
    set_flag('snap-db-redis.config.available')


@when('endpoint.redis.connected')
@when_not('snap-db-redis.redis.available')
def get_redis_data():
    """ Get redis data
    """
    
    status_set('maintenance', 'Getting snap-db-redis.redis')
    redis = flag_from_endpoint('endpoint.redis.available')
    redis.set_database('snap-db-redis.redis')

    KV.set('rdhost', redis.host)
    KV.set('rdport', redis.port)
    KV.set('rddb', redis.databases)

    status_set('active', 'Redis Config Written')
    log('Redis Config Retrieved')
    set_flag('snap-db-redis.redis.available') 

@when('snap-db-redis.redis.available')
@when_not('snap-db-redis.redis.config.available')
def write_redis_data():    
    status_set('maintenance', 'Writting redis config')
    redis_config = KV.getrange('rd')
    redis_db_config = \
        'redis://{dbhost}:{dbport}/{rddb}'.format(**redis_config)

    with open(REDIS_OUT, 'a') as f:
        f.write(redis_db_config)

    status_set('active', redis_config)
    log('Redis DB Config Available')
    set_flag('snap-db-redis.redis.config.available') 







