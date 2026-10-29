import socket

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind(("0.0.0.0", 5000))
s.listen()
print("À espera de ligação...")

conn, addr = s.accept()
print("Ligado por", addr)
dados = conn.recv(1024).decode()
print("Recebido:", dados)
conn.sendall("Olá do servidor!".encode())
conn.close()
s.close()