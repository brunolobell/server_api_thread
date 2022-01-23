from http.server import HTTPServer, BaseHTTPRequestHandler
from socketserver import ThreadingMixIn
from urllib.parse import urlparse
import json, logging, os, threading, requests as req

# Environments Variables 
host = os.getenv('HOST', 'localhost')
port = os.getenv('PORT', 8080)
marketAccessKey = os.getenv('MARKET_KEY', 'd02610aad5a5fed063f8c553ac5df977')

# Class to handle http requests
class Handler(BaseHTTPRequestHandler):
    # Function to requests GET
    def do_GET(self):
        try:
            logging.info("GET request,\nPath: %s\nHeaders:\n%s\n", str(self.path), str(self.headers))
            query = urlparse(self.path).query
            if (len(query) == 0):
                self.send_response(401)
                self.end_headers()
                self.wfile.write(b'Need pass symbol')
                return
            params = dict(qc.split("=") for qc in query.split("&"))
            
            params['access_key'] = marketAccessKey
            # Connect to marketstack api and get response like a JSON
            marketResult = req.get("http://api.marketstack.com/v1/eod", params).json()    
            jsonString = json.dumps(marketResult)
            if 'error' in marketResult:
                self.send_response(500)
                self.wfile.write(jsonString.encode())
                return

            self.send_response(200)
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(jsonString.encode())
        except Exception as e:
            logging.error("Error to get request.\n" + str(e))
            self.send_response(500)
            self.end_headers()
            self.wfile.write(str(e).encode())

# Class http server that handle requests in a new thread
class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
    pass

if __name__ == "__main__":
    print ("Starting server on " + host + " at port " + str(port));
    server = ThreadedHTTPServer((host, port), Handler)
    server.serve_forever()