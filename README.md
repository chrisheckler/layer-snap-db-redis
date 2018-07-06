# layer-snap-db-redis
The purpose of this layer is to gain a deeper understanding of Juju and Reactive programming as a whole.  This layer deploys a flask-gunicorn-nginx snap to Juju and will is supported with PostgreSQL and Redis databases.

My intent is to build this into a fully functional API template with Flask routing code able to be simply dropped in.

## Components of this layer
- Flask-gunicorn-nginx snap (https://github.com/omnivector-solutions/snap-flask-gunicorn-nginx)

- Redis (https://github.com/omnivector-solutions/layer-redis)

- PostrgreSQL
