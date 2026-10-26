import socket

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect(("localhost", 5001))
s.send("LOGIN | ana | 1234".encode())
resposta = s.recv(1024).decode()
print(repr(resposta))
s.close()
