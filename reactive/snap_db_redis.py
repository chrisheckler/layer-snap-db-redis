import os
import os.path

from charms.reactive import (
    when,
    when_not,
    set_flag,
    clear_flag,
    endpoint_from_flag,
    when_any,
)

from charmhelpers.core.hookenv import (
    status_set,
    log,
    network_get,
    open_port,
    config,
)

from charmhelpers.core.host import chownr

from charmhelpers.core import unitdata

from charms.layer.snap import install, refresh

from charms.layer.snap_db_redis import (
    render_flask_secrets,
    SU_CONF_DIR,
    FLASK_SECRETS,
)



SNAP_DB_REDIS_HTTP_PORT = 5000

REDIS_OUT = '/home/ubuntu/redis_config.txt'
PGSQL_OUT = '/home/ubuntu/postgreSQL_config.txt'

KV = unitdata.kv()

############ Snap-db-redis Relations #############
@when('snap.installed.flask-gunicorn-nginx')
@when_not('snap-db-redis.conf.dir.available')
def create_data_api_conf_dir():
    """Ensure config dir exists
    """
    
    if not os.path.isdir(SU_CONF_DIR):
        os.makedirs(SU_CONF_DIR, mode=0o644, exist_ok=True)
    chownr(SU_CONF_DIR, owner='www-data', group='www-data')

    set_flag('snap-db-redis.conf.dir.available')

@when('snap.installed.flask-gunicorn-nginx', 
      'snap-db-redis.conf.dir.available')
@when_not('snap-db-redis.secrets.available')
def render_snap_db_redis_config():
    """ Write out secrets
    """

    status_set('active','Rendering snap-db-redis config')

    ctxt = {
            "DEBUG": False,
            "TESTING": False,
            "SECRET_KEY": os.urandom(24),
            }
    
    render_flask_secrets(ctxt)

    status_set('active','Snap-db-redis config rendered')
    log('Snap_db_redis config rendered')
    set_flag('snap-db-redis.secrets.available')


@when('snap-db-redis.secrets.available')
@when_not('snap-db-redis.running')
def set_active_status():
    """Set status/open port
    """
    status_set('active', "Snap-db-redis is running")
    open_port(SNAP_DB_REDIS_HTTP_PORT)

    log('Snap-db-redis is Running')
    set_flag('snap-db-redis.running')
    clear_flag('snap-db-redis.secrets.available')

############ PostgreSQL Relations ##############

@when('pgsql.connected')
@when_not('snap-db-redis.pgsql.requested')
def request_database():
    """When connection established to postgres,
    request a database.
    """

    status_set('maintenance', 'Requesting PostgreSQL database')
    pgsql = endpoint_from_flag('pgsql.connected')
    pgsql.set_database('snap-db-redis')

    log('Database Available')
    status_set('active', 'pgsql.requested')
    set_flag('snap-db-redis.pgsql.requested')


@when('pgsql.master.available',
      'snap-db-redis.pgsql.requested')
@when_not('snap-db-redis.pgsql.available')
def save_database_connection_info():
    """Save the database connection info to the charm unitdata.
    """

    status_set('maintenance',
               'Getting/Setting snap-db-redis database connection info.')

    pgsql = endpoint_from_flag('pgsql.master.available')

    KV.set('dbname', pgsql.master.dbname)
    KV.set('dbuser', pgsql.master.user)
    KV.set('dbpass', pgsql.master.password)
    KV.set('dbhost', pgsql.master.host)
    KV.set('dbport', pgsql.master.port)

    log('Snap-db-redis Database Available')
    status_set('active', 'Snap-db-redis database available')
    set_flag('snap-db-redis.pgsql.available')


@when('snap-db-redis.pgsql.available')
@when_not('snap-db-redis.debugging.config.available')
def output_database_config():
    """Write out database connection info for debugging
    """

    status_set('maintenance', 'Writing database connection info')
    db_config = KV.getrange('db')

    pgsql_config = \
        'postgresql://{dbuser}:{dbpass}@{dbhost}:{dbport}/{dbname}'.format(
            **db_config)


    with open(PGSQL_OUT, 'a') as f:
        f.write(pgsql_config)

    log('PostgreSQL available')
    status_set('active','Config file written' )
    set_flag('snap-db-redis.debugging.config.available')


################ Redis Relations ######################

@when('endpoint.redis.available')
@when_not('snap-db-redis.redis.available')
def get_redis_data():
    """ Get redis data
    """

    status_set('maintenance', 'Getting data')

    endpoint = endpoint_from_flag('endpoint.redis.available')

    with open(REDIS_OUT, 'a') as f:
        f.write((str(endpoint.relation_data()))) 

    log(str(endpoint.relation_data())) 
    set_flag('snap-db-redis.redis.available')
    status_set('active', 'Redis Config Received')


@when('endpoint.redis.broken')
def broken_flag_clear():
    clear_flag('snap-db-redis.redis.available')



