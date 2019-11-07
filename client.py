# -*- coding: utf-8 -*-

import socket

sock = socket.socket()
sock.connect(("localhost",9090))

sock.send(b"qwerty \n")

data = b""
data = sock.recv(1024)
sock.close()

print (data.decode("utf-8"))

