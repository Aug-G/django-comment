import gevent.monkey
import redis.connection
import os



redis.connection.socket = gevent.socket
from ws4redis.uwsgi_runserver import uWSGIWebsocketServer
application = uWSGIWebsocketServer()