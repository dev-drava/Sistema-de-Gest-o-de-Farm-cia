import socket

srv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
srv.bind(("localhost", 5001))
srv.listen()
print("À espera de ligação...")
conn, addr = srv.accept()
while True:
    dados = conn.recv(1024).decode()
    if not dados:
        break
    print("Recebi:", repr(dados))
    comando = dados.strip().split("|")[0]
    if comando == "LOGIN":
        conn.send("LOGIN_OK|CLIENTE\n".encode())
    elif comando == "COMPRAR":
        conn.send("STOCK_INSUFICIENTE\n".encode())
    else:
        conn.send("ERRO\n".encode())
conn.close()