
from datetime import datetime
import time
import threading


class ReverseProxied(object):
    '''Wrap the application in this middleware and configure the
    front-end server to add these headers, to let you quietly bind
    this to a URL other than / and to an HTTP scheme that is
    different than what is used locally.

    In nginx:
    location /myprefix {
        proxy_pass http://192.168.0.1:5001;
        proxy_set_header Host $host;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Scheme $scheme;
        proxy_set_header X-Script-Name /myprefix;
        }

    :param app: the WSGI application
    '''
    def __init__(self, app):
        self.app = app

    def __call__(self, environ, start_response):
        script_name = environ.get('HTTP_X_SCRIPT_NAME', '')
        if script_name:
            environ['SCRIPT_NAME'] = script_name
            path_info = environ['PATH_INFO']
            if path_info.startswith(script_name):
                environ['PATH_INFO'] = path_info[len(script_name):]

        scheme = environ.get('HTTP_X_SCHEME', '')
        if scheme:
            environ['wsgi.url_scheme'] = scheme
        return self.app(environ, start_response)


def timestamp2isoformat(timestamp):
    """
    This function converts a timestamp (float) to a string in the
    ISO 8061 date format
    """
    date = datetime.fromtimestamp(timestamp)
    return date.isoformat()


class BaseController():

    def __init__(self):
        pass


class Singleton(object):
    __singleton_lock = threading.Lock()
    __singleton_instance = None

    @classmethod
    def instance(cls):
        if not cls.__singleton_instance:
            with cls.__singleton_lock:
                if not cls.__singleton_instance:
                    cls.__singleton_instance = cls()
        return cls.__singleton_instance


class memoized_ttl(object):
    """Decorator that caches a function's return value each time it is called within a TTL
    If called within the TTL and the same arguments, the cached value is returned,
    If called outside the TTL or a different value, a fresh value is returned.
    """
    def __init__(self, ttl):
        self.cache = {}
        self.ttl = ttl
    def __call__(self, f):
        def wrapped_f(*args):
            now = time.time()
            try:
                value, last_update = self.cache[args]
                if self.ttl > 0 and now - last_update > self.ttl:
                    raise AttributeError
                return value
            except (KeyError, AttributeError):
                value = f(*args)
                self.cache[args] = (value, now)
                return value
            except TypeError:
                # uncachable -- for instance, passing a list as an argument.
                # Better to not cache than to blow up entirely.
                return f(*args)
        return wrapped_f
