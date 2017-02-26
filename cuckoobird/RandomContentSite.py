import re
import json
import cgi                      # for parse_header
import random
import binascii
import bson
import tornado.ioloop
import tornado.web
import tornado.httputil
from tornado.web import addslash

#----------------------------------------------------------------------
# To install on Ubuntu under systemd, create a service file:
# File location:
#     ~/.config/systemd/user/test-server.service
# File contents:
#     [Unit]
#     Description=Python test service
#     
#     [Service]
#     Type=simple
#     ExecStart=/usr/bin/python3 -u /home/WHATEVER/RandomContentSite.py
#
# Start:
#     systemctl --user start test-server
# Start:
#     systemctl --user stop test-server
# Log (we ran python3 -u for unbuffered output so it shows immediately in log):
#     /var/log/syslog
#
#----------------------------------------------------------------------
# To install as a Cygwin Windows service, use cygrunsrv as follows.
# Perform the following as administrator.
#
# Install (no userspace drives mapped, use something like /cygdrive/c to find script):
#     cygrunsrv --install testserver
#               --path /usr/bin/python3
#               --args "/cygdrive/c/WHATEVER/RandomContentSite.py"
#               --termsig INT                 # service stop signal (graceful shutdown)
#               --shutsig TERM                # system shutdown signal (fast shutdown)
#               --shutdown                    # stop service at system shutdown
# Start:
#     cygrunsrv -S testserver
# Stop:
#     cygrunsrv -E testserver
# Uninstall:
#     cygrunsrv -R testserver
#
#----------------------------------------------------------------------
# To install as a native Python Windows service, use nssm as follows.
#
# Download nssm at http://nssm.cc/ and unzip, you'll use the correct nssm.exe
# program for your OS (32-bit or 64-bit).
#
# Path:              C:\Apps\Python3\python.exe
# Startup directory: C:\WHATEVER
# Arguments:         RandomContentSite.py
# 
#----------------------------------------------------------------------
# To run directly:
#     python3 RandomContentSite.py
#

import signal
def shutdown_callback ():
    '''Callback to shutdown IOLoop.'''
    io_loop = tornado.ioloop.IOLoop.current ()
    io_loop.stop()

def signal_handler (signum, frame):
    '''Signal handler that adds a callback to shutdown the IOLoop.'''
    io_loop = tornado.ioloop.IOLoop.current ()
    io_loop.add_callback_from_signal (shutdown_callback)

# Register signal handler that will add a callback to shutdown the IOLoop
signal.signal (signal.SIGINT, signal_handler)
signal.signal (signal.SIGTERM, signal_handler)

# Prefix where site runs, can be blank
import sys
site_prefix = ""
port = 8080                       # default to port 8080 if not provided on cmd line
if __name__ == "__main__" and len(sys.argv) > 1 and sys.argv[1] != '':
    site_prefix = "/{}".format (sys.argv[1])
    if len(sys.argv) > 2 and sys.argv[2] != '':
        if re.fullmatch ("\d{1,5}", sys.argv[2]):
            port = int (sys.argv[2])
            if (port < 0 or port > 65535):
                raise Exception ("Port number out of range")
        else:
            raise Exception ("Port number must be a positive integer")
print ("Using port number {}".format (port))

class MainDataHandler (tornado.web.RequestHandler):
    '''
    Handler for getting created random data like /random/12345
    '''
    def initialize(self):
        '''Initializes a new request, params come from dict 3rd param of url spec.'''
        self.mood = "ambivalent"
    def prepare (self):
        '''Common initialization regardless of the request method.'''
        self.site_prefix = site_prefix
        #
        # URLs generated should be prepended with prefix, proxy tells us what url
        # we proxied through
        #
        if (self.site_prefix != ""):
            # Remove it from the uri and path, then readd slash if it becomes empty
            # to be compatible between running directly versus via web proxy
            if self.request.uri.startswith (self.site_prefix):
                self.request.uri = self.request.uri[len(self.site_prefix):]
                if self.request.uri == "":
                    self.request.uri = "/"
                elif len (self.request.uri) > 0 and self.request.uri[0] != "/":
                    self.request.uri = "/" + self.request.uri
            if self.request.path.startswith (self.site_prefix):
                self.request.path = self.request.path[len(self.site_prefix):]
                if self.request.path == "":
                    self.request.path = "/"
    def on_finish (self):
        '''Called after response sent to client.'''
        pass
    def get(self):
        self.set_status (200)
        self.set_header ("Content-type", "text/plain; charset=UTF-8")
        self.set_header ("X-Fun-person", "Joe Smith")
        self.write ("site prefix: {}\n".format (self.site_prefix))
        self.write ("method: {}\n".format (self.request.method))
        self.write ("uri: {}\n".format (self.request.uri))
        self.write ("path: {}\n".format (self.request.path))
        self.write ("query: {}\n".format (self.request.query))
        self.write ("version: {}\n".format (self.request.version))
        self.write ("remote ip: {}\n".format (self.request.remote_ip))
        self.write ("protocol: {}\n".format (self.request.protocol))
        self.write ("headers:\n")
        for (key, value) in sorted (self.request.headers.get_all ()):
            self.write ("    {}={}\n".format (key, value))

class PostDataHandler (tornado.web.RequestHandler):
    '''
    Handler for posting new requests to /random/.
    '''
    def initialize(self):
        '''Initializes a new request, params come from dict 3rd param of url spec.'''
        self.mood = "ambivalent"
    def prepare (self):
        '''Common initialization regardless of the request method.'''
        self.site_prefix = site_prefix
        #
        # URLs generated should be prepended with prefix, proxy tells us what url
        # we proxied through
        #
        if (self.site_prefix != ""):
            # Remove it from the uri and path, then readd slash if it becomes empty
            # to be compatible between running directly versus via web proxy
            if self.request.uri.startswith (self.site_prefix):
                self.request.uri = self.request.uri[len(self.site_prefix):]
                if self.request.uri == "":
                    self.request.uri = "/"
                elif len (self.request.uri) > 0 and self.request.uri[0] != "/":
                    self.request.uri = "/" + self.request.uri
            if self.request.path.startswith (self.site_prefix):
                self.request.path = self.request.path[len(self.site_prefix):]
                if self.request.path == "":
                    self.request.path = "/"
    def on_finish (self):
        '''Called after response sent to client.'''
        pass
    def get(self):
        self.set_status (200)
        self.set_header ("Content-type", "text/plain; charset=UTF-8")
        self.write ("""JSON API to random content:
1. POST to {prefix} to obtain a resource containing random data.
    a.  For example, resource with a random name such as {prefix}/12345 returned.
2. GET the resource you obtained exactly once, upon which it self-destructs.
    a.  For example, GET {prefix}/12345 returns random octets
    b.  Subsequent GET {prefix}/12345 returns 404 Not Found
If GET of the resource results in 404 Not Found, someone got it before you.
""".format (prefix=self.site_prefix));
    def post(self):
        # Get JSON API request
        data = self.request.body

        # Validate request body size
        try:
            if len (data) > 100:
                raise Exception (400, "{'error': 'Request body too large'}")

            content_type_list = self.request.headers.get_list ("Content-Type")
            if content_type_list is None or len (content_type_list) == 0:
                raise Exception (400, "{'error': 'Missing Content-Type'}")

            # Get last Content-Type header, parse last instance of header to get charset
            content_type = self.request.headers.get_list ("Content-Type")[-1]
            data_type, data_params = cgi.parse_header (content_type)
            charset = "UTF-8"       # default charset if user doesn't specify
            if data_params is not None and 'charset' in data_params:
                charset = data_params['charset']

            # Turn JSON body into a string using encoding of the charset user handed us
            data_string = data.decode (charset)
            try:
                user_json = json.loads (data_string)
            except Exception as ex:
                raise Exception (400, "{'error': 'Request body must be a JSON object containing length parameter with int value'}")
            if type(user_json) != dict:
                raise Exception (400, "{'error': 'Request body must be a JSON object'}")
            elif not 'length' in user_json:
                raise Exception (400, "{'error': 'Request body must be a JSON object containing a length parameter'}")

            user_length = user_json['length']
            if user_length < 1 or user_length > 1024:
                raise Exception (400, "{'error': 'You may request 1 to 1024 octets of random data'}")

            self.set_status (200)
            self.set_header ("Content-type", "text/plain; charset=UTF-8")
            self.set_header ("X-Fun-person", "Joe Smith")
            self.write ("Hello, world\n")
            self.write ("length requested: {}\n".format (user_length))
            self.write ("site prefix: {}\n".format (self.site_prefix))
            self.write ("method: {}\n".format (self.request.method))
            self.write ("uri: {}\n".format (self.request.uri))
            self.write ("path: {}\n".format (self.request.path))
            self.write ("request body: {}\n".format (data))
            self.write ("headers:\n")
            for (key, value) in sorted (self.request.headers.get_all ()):
                self.write ("    {}={}\n".format (key, value))
            # Create length octets as a bytearray
            generated_data = bytearray ()
            for index in range (user_length):
                generated_data.append (random.getrandbits (8))
            self.write ("output: {}\n".format (binascii.hexlify (generated_data)))
            # Create MongoDB object with bytes we just generated
            bson_data = bson.binary.Binary (bytes (generated_data))
            # Generate 128-bit hex resource name
            resource_name = "{:X}".format (random.getrandbits (128))
            self.write ("resource: {}\n".format (resource_name))
        except Exception as ex:
            if len (ex.args) == 2:
                status, message = ex.args
            else:
                status = 400
                message = str (ex)
            self.set_status (status)
            self.write (message)

class NotFoundHandler (tornado.web.RequestHandler):
    '''Not found for all http verbs.'''
    def prepare (self):
        '''Common initialization regardless of the request method.'''
        self.send_error (404)

class RedirectToRootHandler (tornado.web.RequestHandler):
    '''Redirect to root resource.'''
    def prepare (self):
        '''Common initialization regardless of the request method.'''
        self.redirect (site_prefix + "/")

patterns = [
    (r"", RedirectToRootHandler),
    (r"/", PostDataHandler),
    (r"/.*", MainDataHandler),
]

#
# If this runs with a certain prefix, pass as cmd arg and we'll prepend it to
# all url patterns (eg, /u becomes /${site_prefix}/u).
#
import sys
if __name__ == "__main__" and site_prefix != '':
    patterns = [(site_prefix + item[0],) + item[1:] for item in patterns]

# Everything outside of the site prefix is not found
patterns.append ((r"/.*", NotFoundHandler))

for item in patterns:
    print ("Pattern: {}".format (item))

application = tornado.web.Application (patterns)

if __name__ == "__main__":
    print ("Application begin, listening on localhost port {}".format (port))
    # Listen locally, proxy handles GET requests for existing files
    application.listen (port, 'localhost')
    tornado.ioloop.IOLoop.current ().start ()
    print ("Application end")
