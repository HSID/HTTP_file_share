#!/usr/bin/env python

import socket
import argparse
import httplib

DEFAULT_REMOTE_HOST = '127.0.0.1'
DEFAULT_REMOTE_PORT = 8080

class HTTPClient:
    def __init__(self, remote_host_name, remote_host_port):
        self.host_name = socket.gethostname()
        self.ip_address = socket.gethostbyname(self.host_name)
        self.remote_host_name = remote_host_name
        self.remote_host_port = remote_host_port

    def login(self):
        userID = raw_input('User ID: ')
        password = raw_input('Password: ')
        http = httplib.HTTPConnection(self.remote_host_name, self.remote_host_port)
        http.putrequest('GET', '/')
        http.putheader('Host', self.ip_address)
        http.putheader('Authorization', ':'.join([userID, password]))
        http.endheaders()
        try:
            http_response = http.getresponse()
        except Exception:
            print 'Client failed'
        else:
            print 'Got message from %s' % self.remote_host_name
        print http_response.getheader('Response-content')
        if http_response.status == 200: return True
        else: return False

    def register(self):
        userID = raw_input('User ID: ')
        password = raw_input('Password: ')
        http = httplib.HTTPConnection(self.remote_host_name, self.remote_host_port)
        http.putrequest('GET', '/')
        http.putheader('Host', self.ip_address)
        http.putheader('Register', ':'.join([userID, password]))
        http.endheaders()
        try:
            http_response = http.getresponse()
        except Exception:
            print 'Client failed'
        else:
            print 'Got message from %s' % self.remote_host_name
        print http_response.getheader('Response-content')
        return False

    def download(self):
        remote_file_path = raw_input('Remote file path: ')
        http = httplib.HTTPConnection(self.remote_host_name, self.remote_host_port)
        http.putrequest('GET', remote_file_path)
        http.putheader('User-Agent', __file__)
        http.putheader('Host', self.remote_host_name)
        http.putheader('Accept', '*/*')
        http.endheaders()

        try:
            http_response = http.getresponse()
        except Exception:
            print 'Client failed'
        else:
            print 'Got file from %s' % self.remote_host_name

        print http_response.getheader('Response-content')
        remote_file = http_response.read()
        dest_file = open(remote_file_path.split('/')[-1], 'w')
        dest_file.write(remote_file)
        dest_file.close()

    def upload(self):
        local_file_path = raw_input('Local file path: ')
        http = httplib.HTTPConnection(self.remote_host_name, self.remote_host_port)
        local_file = open(local_file_path, 'r')
        local_file_content = local_file.read()
        local_file.close()
        http.putrequest('POST', '/' + local_file_path.split('/')[-1])
        http.putheader('User-Agent', __file__)
        http.putheader('Content-length', len(local_file_content))
        http.putheader('Host', self.remote_host_name)
        http.putheader('Accept', '*/*')
        http.endheaders()
        http.send(local_file_content)

        try:
            http_response = http.getresponse()
        except Exception:
            print 'Client failed'
        else:
            print 'Got response from %s' % self.remote_host_name

        print http_response.getheader('Response-content')

    def main_loop(self):
        parser = argparse.ArgumentParser(description='HTTP Client')
        parser.add_argument('--file', action='store', dest='filename', required=False)
    #    given_args = parser.parse_args()

        while True:
            try:
                initTypeString = raw_input('login/register: ')
                init_result = {'login':lambda: self.login(), 'register':lambda: self.register()}[initTypeString]()
                if not init_result: continue
            except KeyError:
                print 'Input error...(login, register)'
                continue
            while True:
                try:
                    requestTypeString = raw_input('Request Type (download, upload): ')
                    {
                        'download':lambda: self.download(),
                        'upload'  :lambda: self.upload()
                    }[requestTypeString]()
                except KeyError:
                    print 'Input error...(download, upload)'
                    continue
                while True:
                    continueFlagString = raw_input('Next step (continue, exit): ');
                    try:
                        {
                            'continue':lambda x : None,
                            'exit'    :lambda x : exit(x)
                        }[continueFlagString](1)
                    except KeyError:
                        print 'Input error...(continue, exit)'
                        continue
                    break

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='HTTP Client')
    parser.add_argument('--host', action='store', dest='remote_host', default=DEFAULT_REMOTE_HOST)
    parser.add_argument('--port', action='store', dest='remote_port', type=int,  default=DEFAULT_REMOTE_PORT)
    given_args = parser.parse_args()
    host, port = given_args.remote_host, given_args.remote_port
    client = HTTPClient(host, port)
    client.main_loop()

