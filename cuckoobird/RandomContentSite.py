import os
import sys
import getpass
import re
import json
import cgi                      # for parse_header
import random
import binascii
import datetime
import bson.binary
import tornado.ioloop
import tornado.web
import tornado.httputil
import tornado.options
from tornado.web import addslash
import pymongo

#----------------------------------------------------------------------
# Configuration file
#
# Create a simple name=value style configuration file that gets loaded, to provide
# the database host, port, database name, username, and password, such as:
#     db_host = "localhost"
#     db_port = 27017
#     db_name = "rand"
#     db_user = "myuser"
#     db_password = "SECRET"
# Omit db_user to connect unauthenticated (probably a very bad idea).
#
#----------------------------------------------------------------------
# Testing using curl
#
# Post to obtain 10 octets of random data:
#     $ curl -i -X POST 'http://localhost:8080/random/' -H 'Content-Type: application/json' --data-binary '{"length": 10}'
#
# Get of random data created, using resource name returned from post:
#     $ curl -i 'http://localhost:8080/random/A274CB0A2816135DD4FD92FEFA1009F'
#----------------------------------------------------------------------

print ("Application begin")

# Globals
client = None
database = None
collection = None

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
        # Find the resource (strip leading slash)
        resource = self.request.uri[1:]
        # Obtain document
        document = collection.find_one ({"_id": resource})
        if not document:
            self.set_status (404)
        else:
            # Update access count on document
            result = collection.update_one ({"_id": resource}, {"$inc": {"access_count": 1}})
            if result.modified_count == 0:
                # Log and ignore error
                print ("Internal error, unable to update access_count on resource {}".format (resource))
            # Ensure resource lookup count limited to one access
            if document["access_count"] > 0:
                self.set_status (404)
            else:
                self.set_status (200)
                self.set_header ("Content-type", "application/json")
                valueBytes = document["randomdata"]
                # Write binary as base64
                self.write ("{{\"data-base64\": \"{}\"}}\n".format (binascii.b2a_base64 (valueBytes).decode ('utf-8').strip ()))

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
                raise Exception (400, '{"error": "Request body too large"}')

            content_type_list = self.request.headers.get_list ("Content-Type")
            if content_type_list is None or len (content_type_list) == 0:
                raise Exception (400, '{"error": "Missing Content-Type"}')

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
                raise Exception (400, '{"error": "Request body must be a JSON object containing length parameter with int value"}')
            if type(user_json) != dict:
                raise Exception (400, '{"error": "Request body must be a JSON object"}')
            elif not 'length' in user_json:
                raise Exception (400, '{"error": "Request body must be a JSON object containing a length parameter"}')

            user_length = user_json['length']
            if not type (user_length) is int:
                raise Exception (400, '{"error": "Request body must be a JSON object containing length parameter with int value"}')
            if user_length < 1 or user_length > 1024:
                raise Exception (400, '{"error": "You may request 1 to 1024 octets of random data"}')

            self.set_status (200)
            self.set_header ("Content-type", "application/json")
            # Create length octets as a bytearray
            generated_data = bytearray ()
            for index in range (user_length):
                generated_data.append (random.getrandbits (8))
            # Create MongoDB object with bytes we just generated
            bson_data = bson.binary.Binary (bytes (generated_data))
            # Generate 128-bit hex resource name
            resource_name = "{:X}".format (random.getrandbits (128))
            # Write output as resource name and base64 of data generated
            self.write ("{{\"resource\": \"{}\", \"data-base64\": \"{}\"}}\n".format (
                resource_name, binascii.b2a_base64 (generated_data).decode ('utf-8').strip ()))
            # Try to write to database the generated_data stored under resource_name
            document = dict ()
            document["_id"] = resource_name     # Resource name is object ID
            document["access_count"] = 0        # Count of times resource looked up
            document["create_date"] = datetime.datetime.utcnow ()
            document["randomdata"] = bson_data  # Resource data
            collection.insert_one (document)
        except Exception as ex:
            if len (ex.args) == 2:
                status, message = ex.args
            else:
                status = 400
                message = str (ex)
            self.set_status (status)
            self.set_header ("Content-type", "application/json")
            self.write (message)
            self.write ("\n")

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
if __name__ == "__main__" and site_prefix != '':
    patterns = [(site_prefix + item[0],) + item[1:] for item in patterns]

# After prepending prefix, everything outside of the site prefix is not found
patterns.append ((r"/.*", NotFoundHandler))

for item in patterns:
    print ("Pattern: {}".format (item))

application = tornado.web.Application (patterns)

def maintenance ():
    # Remove rows older than 5 minutes
    five_min_ago = datetime.datetime.utcnow () - datetime.timedelta (minutes=5)
    result = collection.delete_many ({"create_date": {"$lt": five_min_ago}})
    if (result.deleted_count > 0):
        print ("Removed {} old documents".format (result.deleted_count))
    # Remove documents accessed once or more times
    result = collection.delete_many ({"access_count": {"$gt": 0}})
    if (result.deleted_count > 0):
        print ("Removed {} completed access documents".format (result.deleted_count))
    
if __name__ == "__main__":
    # Setup options to read from site.ini
    tornado.options.define ("db_host", type=str, default="localhost")
    tornado.options.define ("db_port", type=int, default=27017)
    tornado.options.define ("db_name", type=str)
    tornado.options.define ("db_user", type=str)
    tornado.options.define ("db_password", type=str)
    tornado.options.parse_config_file ("site.ini")
    config = tornado.options.options

    try:
        print ("Connecting to database host {} port {}".format (
            config.db_host, config.db_port))
        client = pymongo.MongoClient (
            host=config.db_host, port=config.db_port,
            maxIdleTimeMS=60000,       # max time connection is idle before removal
            connectTimeoutMS=10000,    # initial connection timeout
            socketTimeoutMS=60000      # response timeout
        )
        client.admin.command ('ping')
        info = client.server_info ()
        print ("Database server version {}".format (info['version']))
        # Get database and names of collections
        database = client[config.db_name]
        # Try authenticating against the database
        if (config.db_user is not None and config.db_user != ""):
            print ("Authenticating as user {}".format (config.db_user))
            database.authenticate (config.db_user, config.db_password)
            print ("    authenticated to database '{}' as user '{}'".format (config.db_name, config.db_user))
        else:
            print ("Not using database authentication")
        # Show collections
        names = database.collection_names ()
        print ("Database '{}' has {} collections".format (config.db_name, len (names)))
        # Obtain a pymongo.collection.Collection (or simply database.randomdata)
        collection = database.get_collection ("randomdata")
        print ("Collection 'randomdata' count: {}".format (collection.count ()))
    except pymongo.errors.InvalidName as ex:
        raise SystemExit ("Invalid database name: {}".format (str (ex)))
    except Exception as ex:
        raise SystemExit ("Problem connecting to database: {}".format (str (ex)))

    print ("Application begin, listening on localhost port {}".format (port))

    # Start periodic maintenance task in the background
    maint_seconds = 5
    maint = tornado.ioloop.PeriodicCallback (maintenance, maint_seconds * 1000)
    print ("Scheduling maintenance task every {} seconds".format (maint_seconds))
    maint.start ()

    # Listen locally, proxy handles GET requests for existing files
    application.listen (port, 'localhost')
    tornado.ioloop.IOLoop.current ().start ()

    print ("Stopping maintenance task")
    maint.stop ()
    print ("Closing database connection")
    client.close ()
    print ("Application end")
