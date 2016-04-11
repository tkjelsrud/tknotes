import http.server
import socketserver
import pprint
import json
import re
import urllib.parse
from json import JSONEncoder
import sys

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
        self.scope = 0
        self.style = ""
        self.props = {}
    def __str__(self):
        return str(self.id) + " " + str(self.scope) + " " + self.text
        
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
            n.props = no.get('props', {})
            
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
                Memory.notes[i] = note
                #print("Did update")
                return True
        #print("Did not find " + str(note))
        #if len(Memory.notes) > 0:
        #    print(" in " + str(Memory.notes[0]))
        Memory.notes.append(note)   
        return True        
            
    @staticmethod
    def toDisk():
        nData = {'notes': [], 'scopes': []}
        w = 0
        ws = 0
        for n in Memory.notes:
            nData['notes'].append(n)
            w = w + 1
        
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
                    if int(n.scope) == int(scope):
                        nData['notes'].append(n)
                self.respond(MyEncoder().encode(nData))
            
            if(self.path.startswith("/scopes/")):
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

print("serving at port", PORT)
httpd.serve_forever()