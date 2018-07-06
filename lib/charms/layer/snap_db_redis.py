import os

from jinja2 import (
    Environment,
    FileSystemLoader
)

from charmhelpers.core import unitdata
from charmhelpers.core.hookenv import charm_dir


SU_CONF_DIR = os.path.join('/', 'home', 'ubuntu')

FLASK_SECRETS = os.path.join(SU_CONF_DIR, 'flask_secrets.py')


kv = unitdata.kv()


def render_flask_secrets(secrets=None):
    """Render flask secrets
    """
    if secrets:
        secrets = secrets
    else:
        secrets = {}

    # Render config source and target
    if os.path.exists(FLASK_SECRETS):
        os.remove(FLASK_SECRETS)

    app_yml = load_template('flask_secrets.py.j2')
    app_yml = app_yml.render(secrets=return_secrets(secrets))

    # Spew configs into source
    spew(FLASK_SECRETS, app_yml)
    os.chmod(os.path.dirname(SU_CONF_DIR), 0o755)


def load_template(name, path=None):
    """ load template file
    :param str name: name of template file
    :param str path: alternate location of template location
    """
    if path is None:
        path = os.path.join(charm_dir(), 'templates')
    env = Environment(
        loader=FileSystemLoader(path))
    return env.get_template(name)


def spew(path, data):
    """ Writes data to path
    :param str path: path of file to write to
    :param str data: contents to write
    """
    with open(path, 'w') as f:
        f.write(data)


def return_secrets(secrets=None):
    """Return secrets dict
    """

    if secrets:
        secrets_mod = secrets
    else:
        secrets_mod = {}

    secrets_mod['REDIS_HOST'] = kv.get('redis_host')
    secrets_mod['REDIS_PORT'] = kv.get('redis_port')

    return secrets_mod
