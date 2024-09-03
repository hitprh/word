#!/usr/bin/python
import socket
import threading
import select
import sys
import time

# Listen and Target Configurations
PORT_HOST_MAPPING = {
    8443: '127.0.0.1:443',
    9443: '127.0.0.1:443',
    7443: '127.0.0.1:443',
    80: '127.0.0.1:550',
    3128: '127.0.0.1:550',
    8888: '127.0.0.1:550'
}

# Pass
PASS = ''

# CONST
BUFLEN = 4096 * 4
TIMEOUT = 500000
RESPONSE = 'HTTP/1.1 101 <b><font color="#FF9800">MK DURAN</font></b>\r\n\r\nContent-Length: 104857600000\r\n\r\n'

class Server(threading.Thread):
    def __init__(self, host, port, target_host):
        threading.Thread.__init__(self)
        self.running = False
        self.host = host
        self.port = port
        self.target_host = target_host
        self.threads = []
        self.threadsLock = threading.Lock()
        self.logLock = threading.Lock()

    def run(self):
        self.soc = socket.socket(socket.AF_INET)
        self.soc.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.soc.settimeout(2)
        self.soc.bind((self.host, self.port))
        self.soc.listen(0)
        self.running = True

        print(f"Server listening on {self.host}:{self.port} and forwarding to {self.target_host}")

        try:
            while self.running:
                try:
                    c, addr = self.soc.accept()
                    c.setblocking(1)
                except socket.timeout:
                    continue

                conn = ConnectionHandler(c, self, addr, self.target_host)
                conn.start()
                self.addConn(conn)
        finally:
            self.running = False
            self.soc.close()
            print(f"Server on {self.host}:{self.port} stopped")

    def printLog(self, log):
        with self.logLock:
            print(log)

    def addConn(self, conn):
        with self.threadsLock:
            if self.running:
                self.threads.append(conn)

    def removeConn(self, conn):
        with self.threadsLock:
            self.threads.remove(conn)

    def close(self):
        self.running = False
        with self.threadsLock:
            threads = list(self.threads)
            for c in threads:
                c.close()

class ConnectionHandler(threading.Thread):
    def __init__(self, socClient, server, addr, target_host):
        threading.Thread.__init__(self)
        self.clientClosed = False
        self.targetClosed = True
        self.client = socClient
        self.client_buffer = ''
        self.server = server
        self.target_host = target_host
        self.log = f"Connection: {addr}"

    def close(self):
        try:
            if not self.clientClosed:
                self.client.shutdown(socket.SHUT_RDWR)
                self.client.close()
        except:
            pass
        finally:
            self.clientClosed = True

        try:
            if not self.targetClosed:
                self.target.shutdown(socket.SHUT_RDWR)
                self.target.close()
        except:
            pass
        finally:
            self.targetClosed = True

    def run(self):
        try:
            self.client_buffer = self.client.recv(BUFLEN)
            self.method_CONNECT(self.target_host)
        except Exception as e:
            self.log += f" - error: {str(e)}"
            self.server.printLog(self.log)
        finally:
            self.close()
            self.server.removeConn(self)

    def connect_target(self, host):
        i = host.find(':')
        if i != -1:
            port = int(host[i+1:])
            host = host[:i]
        else:
            port = 443

        (soc_family, soc_type, proto, _, address) = socket.getaddrinfo(host, port)[0]
        self.target = socket.socket(soc_family, soc_type, proto)
        self.targetClosed = False
        self.target.connect(address)

    def method_CONNECT(self, path):
        self.log += f" - CONNECT {path}"

        self.connect_target(path)
        self.client.sendall(RESPONSE.encode('utf-8'))
        self.client_buffer = ''

        self.server.printLog(self.log)
        self.doCONNECT()

    def doCONNECT(self):
        socs = [self.client, self.target]
        count = 0
        error = False
        while True:
            count += 1
            (recv, _, err) = select.select(socs, [], socs, 3)
            if err:
                error = True
            if recv:
                for in_ in recv:
                    try:
                        data = in_.recv(BUFLEN)
                        if data:
                            if in_ is self.target:
                                self.client.send(data)
                            else:
                                self.target.send(data)
                            count = 0
                        else:
                            break
                    except:
                        error = True
                        break
            if count == TIMEOUT:
                error = True
            if error:
                break

def main():
    servers = []
    for port, target_host in PORT_HOST_MAPPING.items():
        server = Server('0.0.0.0', port, target_host)
        servers.append(server)
        server.start()

    try:
        while True:
            time.sleep(2)
    except KeyboardInterrupt:
        print('Stopping...')
        for server in servers:
            server.close()

if __name__ == '__main__':
    main()