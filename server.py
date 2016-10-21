
import http.server
#from BaseHTTPServer import BaseHTTPRequestHandler
from datetime import datetime
import ssl
import socketserver
import pprint
import json
import re
import os
import urllib.parse
from json import JSONEncoder
import sys

print("Hello world", os.environ.get('PORT'))

"""
from http.server import HTTPServer,SimpleHTTPRequestHandler
from socketserver import BaseServer
import ssl
httpd = HTTPServer(('localhost', 1443), SimpleHTTPRequestHandler)

ssl.verify_mode = ssl.CERT_NONE
httpd.socket = ssl.wrap_socket (httpd.socket, keyfile='localhost.key.pem', certfile='localhost.cert.pem', server_side=True)
httpd.serve_forever()
"""





PORT = os.environ.get('PORT', 5000)
DFILE = 'tknotes_data.json'

class MyEncoder(JSONEncoder):
    def default(self, o):
        return o.__dict__   

class Event:
    def __init__(self, key, value):
        self.date = str(datetime.now())
        self.key = key
        self.value = value
    
    def __str__(self):
        return self.date + " " + self.key + " " + self.value
        
class Note:
    def __init__(self, id):
        self.id = id;
        self.text = "aksjdhaskjdhasd"
        self.pos = [0, 0]
        self.scope = 0
        self.style = ""
        self.props = {}
        self.delete = 0
        self.nclass = ""
        self.events = []
        self.secured = 0
        
    def __str__(self):
        return str(self.id) + " " + str(self.scope) + " " + self.text

    def updateFrom(self, note):
        # Update with another note ("safe overwrite")
        # Not touching the events
        self.pos = note.pos
        self.text = note.text
        self.scope = note.scope
        self.style = note.style
        self.props = note.props
        self.delete = note.delete
        self.nclass = note.nclass
        self.secured = note.secured
        
    def addEvent(self, key, value):
        self.events.append(Event(key, value))
        
    def hasEvent(self, key):
        for e in self.events:
            if key == e.key:
                return True
        return False
        
class Memory:
    notes = []
    scopes = []
    
    @staticmethod
    def fromJson(json):
        for no in json['notes']:
            n = Note(no['id'])
            n.text = no['text']
            n.pos = no['pos']
            n.scope = no.get('scope', 0)
            n.style = no.get('style', "")
            n.delete = int(no.get('delete', 0))
            n.nclass = no.get('nclass', "")
            n.props = no.get('props', {})
            n.secured = no.get('secured', 0)
            
            Memory.addOrUpdate(n)
        
        if 'scopes' in json:
            for sc in json['scopes']:
                print(str(sc))
                Memory.scopes.append({'id': sc.get('id'), 'name': sc.get('name')})
    
    @staticmethod
    def addOrUpdate(note):
        for i in range(0, len(Memory.notes)):
            n = Memory.notes[i]
            #print(str(n) + " vs " + str(note))
            if int(n.id) == int(note.id) and int(n.scope) == int(note.scope):
                Memory.notes[i].updateFrom(note)
                #print("Did update")
                return True
        
        if not note.hasEvent("CREATED"):
            note.addEvent("CREATED", "")
        
        Memory.notes.append(note)   
        return True        
            
    @staticmethod
    def toDisk():
        nData = {'notes': [], 'scopes': []}
        w = 0
        ws = 0
        for n in Memory.notes:
            if(n.delete == 0):
                nData['notes'].append(n)
                w = w + 1
            else:
                print("DELETE " + str(n.id))
        
        for n in Memory.scopes:
            nData['scopes'].append(n)
            ws = ws + 1
        
        f = open(DFILE, 'w')
        f.write(MyEncoder().encode(nData))
        f.close()
        print('Wrote notes:' + str(w) + ' scopes:' + str(ws) + ' to:' + DFILE)
     
    @staticmethod
    def fromDisk():
        try:
            f = open(DFILE, 'r')
            data = json.loads(f.read())
            f.close()
            Memory.fromJson(data)
            print('Read ' + str(len(Memory.notes)) + ' from disk')
        except Exception as e:
            print("Error" + str(e))
            
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
                uAr = self.path.split("?")
                ar = uAr[0].split("/")
                scope = 1
                
                if int(ar[len(ar) - 1]) > 0:
                    scope = int(ar[len(ar) - 1])
                
                nData = {'notes': []}
                for n in Memory.notes:
                    if int(n.scope) == int(scope) and n.delete == 0:
                        nData['notes'].append(n)
                self.respond(MyEncoder().encode(nData))
            
            elif(self.path.startswith("/scopes/")):
                # Auth based on user?
                nData = {'scopes': []}
                for n in Memory.scopes:
                    nData['scopes'].append(n)
                self.respond(MyEncoder().encode(nData))
            
            if not self.responded:
                # Default response
                http.server.SimpleHTTPRequestHandler.do_GET(self)
        
        except:
            print("Unexpected error:" + str(sys.exc_info()[0]))
            raise

Memory.fromDisk()
httpd = socketserver.TCPServer(("", PORT), Handler)

"""
httpd = BaseHTTPServer.HTTPServer(('localhost', 4443), SimpleHTTPServer.SimpleHTTPRequestHandler)
httpd.socket = ssl.wrap_socket (httpd.socket, certfile='path/to/localhost.pem', server_side=True)
httpd.serve_forever()
"""


print("serving at port", PORT)
httpd.serve_forever()
