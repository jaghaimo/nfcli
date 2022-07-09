import gevent
import gevent.monkey

gevent.monkey.patch_socket()
gevent.monkey.patch_select()
gevent.monkey.patch_ssl()
