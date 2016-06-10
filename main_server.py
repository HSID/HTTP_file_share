#!/usr/bin/env python

import os
import socket
import argparse
from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer

DEFAULT_HOST = '127.0.0.1'
DEFAULT_PORT = 8080

userFile = open('userList', 'r')
userDict = {}
while True:
    line = userFile.readline()
    if not line: break
    (userID, password) = line.split()
    userDict[userID] = password
userFile.close()

currentUserDict = {}

class HTTPRequestHandler(BaseHTTPRequestHandler):
    def __init__(self, request, client_address, server):
        BaseHTTPRequestHandler.__init__(self, request, client_address, server)
        self.host_name = socket.gethostname()
        self.ip_address = socket.gethostbyname(self.host_name)

    def send_requested_file(self):
        try:
            requestedFile = open(self.path, 'r')
            fileContent = requestedFile.read()
            requestedFile.close()
            self.send_response(200)
            self.send_header('Content-type', 'image')
            self.send_header('Response-content', 'File-sended')
            self.end_headers()
            self.wfile.write(fileContent)
        except IOError:
            self.send_response(404)
            self.send_header('Response-content', 'No-such-file')
            self.end_headers()

    def send_auth_fail_response(self, fail_reason):
        self.send_response(401)
        self.send_header('Response-content', fail_reason)
        self.end_headers()

    def send_auth_success_response(self):
        self.send_response(200)
        self.send_header('Response-content', 'Authenticate-success')
        self.end_headers()

    def send_reg_success_response(self):
        self.send_response(200)
        self.send_header('Response-content', 'Register-success')
        self.end_headers()

    def send_upload_success_response(self):
        self.send_response(200)
        self.send_header('Response-content', 'Upload-success')
        self.end_headers()

#    def do_GET(self):
#        self.send_response(200)
#        self.send_header('Content-type', 'text/html')
#        self.end_headers()
#        self.wfile.write('Hello')

    def do_GET(self):
        (ip_address, localPort) = self.client_address
        if ip_address in currentUserDict.keys():
# Already login, serve as normal.
            self.path = './' + currentUserDict[ip_address] + self.path
            self.send_requested_file()
        elif self.headers.getheaders('Authorization'):
# Match the authentication info
            (client_userID, client_password) = self.headers.getheaders('Authorization')[0].split(':')
            print client_userID, client_password
            if client_userID in userDict.keys():
                if userDict[client_userID] == client_password:
                    currentUserDict[ip_address] = client_userID
                    self.send_auth_success_response()
                else:
                    self.send_auth_fail_response('Wrong-Password')
            else:
                self.send_auth_fail_response('Wrong-UserID')
        elif self.headers.getheaders('Register'):
            (client_userID, client_password) = self.headers.getheaders('Register')[0].split(':')
            print client_userID, client_password
            userDict[client_userID] = client_password
            os.mkdir('./' + client_userID)
            self.send_reg_success_response()
        else:
            self.send_auth_fail_response('Authentication-Required')


    def do_POST(self):
        (ip_address, localPort) = self.client_address
        if ip_address in currentUserDict.keys():
            self.path = './' + currentUserDict[ip_address] + '/' + self.path.split('/')[-1]
            recv_file = self.rfile.read(int(self.headers.getheaders('Content-length')[0]))
            print recv_file
            dest_file = open(self.path, 'w')
            dest_file.write(recv_file)
            dest_file.close()
            self.send_upload_success_response()
        else:
            self.send_auth_fail_response('Authentication-Required')


class CustomHTTPServer(HTTPServer):
    def __init__(self, host, port):
        server_address = (host, port)
        HTTPServer.__init__(self, server_address, HTTPRequestHandler)

def run_server(port):
    try:
        server = CustomHTTPServer(DEFAULT_HOST, port)
        print 'Custom HTTP server started on port: %s' % port
        server.serve_forever()
    except Exception, err:
        print 'Error:%s' % err
    except KeyboardInterrupt:
        userFile = open('userList', 'w')
        for userID in userDict.keys():
            userFile.write(userID + ' ' + userDict[userID] + '\n')
        userFile.close()
        print 'Server interrupted and is shutting down...'
        server.socket.close()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='HTTP Server')
    parser.add_argument('--port', action='store', dest='port', type=int, default=DEFAULT_PORT)
    given_args = parser.parse_args()
    port = given_args.port
    run_server(port)
