import http.server
import socketserver
import pprint
import json
import urllib.parse
from json import JSONEncoder
import sys

#from concept import *

PORT = 8000
DFILE = 'tknotes_data.json'

class MyEncoder(JSONEncoder):
    def default(self, o):
        return o.__dict__   

class Note:
    def __init__(self, id):
        self.id = id;
        self.text = "aksjdhaskjdhasd"
        self.pos = [0, 0]
        
class Memory:
    notes = []
    
    @staticmethod
    def fromJson(json):
        Memory.notes = []
        for no in json['notes']:
            n = Note(no['id'])
            n.text = no['text']
            n.pos = no['pos']
            Memory.notes.append(n)
            
    @staticmethod
    def toDisk():
        nData = {'notes': []}
        for n in Memory.notes:
            nData['notes'].append(n)
        
        f = open(DFILE, 'w')
        f.write(MyEncoder().encode(nData))
        f.close()
        print('Wrote notes to ' + DFILE)
     
    @staticmethod
    def fromDisk():
        try:
            f = open(DFILE, 'r')
            data = json.loads(f.read())
            f.close()
            Memory.fromJson(data)
            print('Read ' + str(len(Memory.notes)) + ' from disk')
        except:
            print("Error")

class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, request, client_address, server):
        #self.request = request
        #self.client = client_address
        #self.server = server
        self.responded = False
        http.server.SimpleHTTPRequestHandler.__init__(self, request, client_address, server)
        
        
    def respond(self, content):
        self.send_response(200)
        self.send_header("Content-type", "application/json")
        self.end_headers()
        self.wfile.write(bytes(content, 'UTF-8'))
        
        self.responded = True

    def do_POST(self):
        try:
            if(self.path.startswith("/notes/")):
                rSize = int(self.headers["Content-Length"])
                data = self.rfile.read(rSize)
                
                jnotes = json.loads(data.decode('utf-8'))
                Memory.fromJson(jnotes)
                Memory.toDisk()
                
                self.respond('OK ' + str(rSize)) #post_body)
                    
            
            if not self.responded:
                # Default response
                http.server.SimpleHTTPRequestHandler.do_POST(self)
        
        except:
            print("Unexpected error:" + str(sys.exc_info()[0]))
            raise
        
    def do_GET(self):    
        try:
            if(self.path.startswith("/notes/")):
                nData = {'notes': []}
                for n in Memory.notes:
                    nData['notes'].append(n)
                self.respond(MyEncoder().encode(nData))
            
            if not self.responded:
                # Default response
                http.server.SimpleHTTPRequestHandler.do_GET(self)
        
        except:
            print("Unexpected error:" + str(sys.exc_info()[0]))
            raise

Memory.fromDisk()
httpd = socketserver.TCPServer(("", PORT), Handler)

print("serving at port", PORT)
httpd.serve_forever()