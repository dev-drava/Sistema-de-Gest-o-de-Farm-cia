import socket
import json
from connect_db import start_connection

HOST = "http://gateway01.ap-southeast-1.prod.alicloud.tidbcloud.com/"
PORT = 4000

def iniciar_sockets():
    servidor = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    servidor.bind((HOST, PORT))
    servidor.listen(1)
    print("servidor à escuta")

    while True:
        conn, addr = servidor.accept()
        dados = json.loads(conn.recv(1024).decode('utf-8'))
        
        acao = dados.get("acao")
        resposta = {"status": "ERRO"}

        conexao = start_connection()
        cursor = conexao.cursor(dictionary=True)

        if acao == "listar":
            cursor.execute("SELECT * FROM medicamentos")
            resposta = {"status": "SUCESSO", "dados": cursor.fetchall()}
            for m in resposta["dados"]:
                if m.get("validade"):
                    m["validade"] = str(m["validade"])

        cursor.close()
        conexao.close()

        conn.send(json.dumps(resposta).encode('utf-8'))
        conn.close()

if __name__ == "__main__":
    iniciar_servidor()