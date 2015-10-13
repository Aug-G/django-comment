from gevent import socket
import redis.connection
import os

redis.connection.socket = socket
from ws4redis.uwsgi_runserver import uWSGIWebsocketServer
application = uWSGIWebsocketServer()