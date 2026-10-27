import socket

srv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
srv.bind(("localhost", 5001))
srv.listen()

while True:
    print("À espera de ligação...")
    conn, addr = srv.accept()
    while True:
        dados = conn.recv(1024).decode()
        if not dados:
            break
        print("Recebi:", repr(dados))
        partes = dados.strip().split("|")
        comando = partes[0]
        if comando == "LOGIN":
            conn.send("LOGIN_OK|CLIENTE\n".encode())
        elif comando == "LISTAR_MEDICAMENTOS":
            conn.send("OK|1,Paracetamol,2.50,10;2,Ibuprofeno,3.20,0\n".encode())
        elif comando == "COMPRAR":
            if int(partes[2]) <= 5:
                conn.send("COMPRA_CONFIRMADA\n".encode())
            else:
                conn.send("STOCK_INSUFICIENTE\n".encode())
        else:
            conn.send("ERRO\n".encode())
    conn.close()