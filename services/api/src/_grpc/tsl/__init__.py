import os

def _load_from_file( path ):
    path = os.path.join( os.path.dirname( __file__ ), path )
    with open( path, "rb" ) as f:
        return f.read()

ROOT_CERTIFICATES = _load_from_file( "server.crt" )
CLIENT_CERTIFICATE = _load_from_file( "client.crt" )
CLIENT_KEY = _load_from_file( "server.key" )