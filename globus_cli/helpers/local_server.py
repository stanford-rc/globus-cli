import logging
import os
import threading

try:
    import http.client as http_client
except ImportError:
    import httplib as http_client

try:
    from BaseHTTPServer import HTTPServer, BaseHTTPRequestHandler
except ImportError:
    from http.server import HTTPServer, BaseHTTPRequestHandler

try:
    import Queue
except ImportError:
    import queue as Queue

try:
    from urlparse import urlparse, parse_qsl
except ImportError:
    from urllib.parse import urlparse, parse_qsl


class LocalServerError(Exception):
    pass


def enable_requests_logging():
    http_client.HTTPConnection.debuglevel = 4

    logging.basicConfig()
    logging.getLogger().setLevel(logging.DEBUG)
    requests_log = logging.getLogger('requests.packages.urllib3')
    requests_log.setLevel(logging.DEBUG)
    requests_log.propagate = True


def is_remote_session():
    return os.environ.get('SSH_TTY', os.environ.get('SSH_CONNECTION'))


class RedirectHandler(BaseHTTPRequestHandler):

        def do_GET(self): # noqa
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(b'You\'re all set, you can close this window!')

            query_params = dict(parse_qsl(urlparse(self.path).query))
            code = query_params.get('code')
            if code:
                self.server.return_code(code)
            else:
                msg = query_params.get(
                    'error_description', query_params.get('error'))

                self.server.return_code(LocalServerError(msg))

        def log_message(self, format, *args):
            return


class RedirectHTTPServer(HTTPServer, object):

    def __init__(self, listen, handler_class):
        super(RedirectHTTPServer, self).__init__(listen, handler_class)

        self._auth_code_queue = Queue.Queue()

    def return_code(self, code):
        self._auth_code_queue.put_nowait(code)

    def wait_for_code(self):
        return self._auth_code_queue.get(block=True)


def start_local_server(listen=('', 0)):
    server = RedirectHTTPServer(listen, RedirectHandler)
    thread = threading.Thread(target=server.serve_forever)
    thread.daemon = True
    thread.start()

    return server
