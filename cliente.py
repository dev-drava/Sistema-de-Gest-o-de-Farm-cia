import socket

HOST = "localhost"
PORTA = 5001


def ligar():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((HOST, PORTA))
    return s


def pedir(s, *partes):
    """Envia COMANDO|arg1|arg2... e devolve a resposta como lista de campos."""
    mensagem = "|".join(str(p) for p in partes) + "\n"
    s.send(mensagem.encode())
    resposta = s.recv(1024).decode().strip()
    return resposta.split("|")



if __name__ == "__main__":
    s = ligar()
    resp_login = pedir(s, "LOGIN", "ana", "1234")
    resp_compra = pedir(s, "COMPRAR", 3, 2)
    print(resp_login)
    print(resp_compra)
    s.close()   