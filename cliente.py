import socket

HOST = "localhost"
PORTA = 5001


def ligar():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((HOST, PORTA))
    return s


def pedir(s, *partes):
    mensagem = "|".join(str(p) for p in partes) + "\n"
    s.send(mensagem.encode())
    resposta = s.recv(1024).decode().strip()
    return resposta.split("|")


def ler_opcao(prompt, minimo, maximo):
    while True:
        texto = input(prompt).strip()
        if texto.isdigit() and minimo <= int(texto) <= maximo:
            return int(texto)
        print("Opção inválida.")


def ler_texto(prompt):
    while True:
        texto = input(prompt).strip()
        if texto and "|" not in texto:
            return texto
        print("Texto inválido.")

def menu_cliente(s):
    while True:
        print("\n CLIENTE \n1) Ver medicamentos\n2) Comprar\n0) Logout")
        op = ler_opcao("> ", 0, 2)
        if op == 1:
            resp = pedir(s, "LISTAR_MEDICAMENTOS")
            print(resp)
        elif op == 2:
            id_med = ler_opcao("ID do medicamento: ", 1, 9999)
            qtd = ler_opcao("Quantidade: ", 1, 9999)
            resp = pedir(s, "COMPRAR", id_med, qtd)
            mostrar(resp)
        else:
            return


def menu_farmaceutico(s):
    print("Menu farmacêutico (em construção)")


def menu_admin(s):
    print("Menu admin (em construção)")


MENUS = {
    "ADMIN": menu_admin,
    "FARMACEUTICO": menu_farmaceutico,
    "CLIENTE": menu_cliente,
}

MENSAGENS = {
    "COMPRA_CONFIRMADA": "Compra efetuada com sucesso.",
    "STOCK_INSUFICIENTE": "Não há stock suficiente.",
    "ERRO": "Ocorreu um erro no servidor.",
}


def mostrar(resp):
    codigo = resp[0]
    print(MENSAGENS.get(codigo, "Resposta do servidor: " + "|".join(resp)))

def fazer_login(s):
    user = ler_texto("Utilizador: ")
    pw = ler_texto("Password: ")
    resp = pedir(s, "LOGIN", user, pw)
    if resp[0] == "LOGIN_OK" and len(resp) > 1:
        papel = resp[1].upper()
        menu = MENUS.get(papel)
        if menu is None:
            print("Papel desconhecido:", papel)
        else:
            menu(s)
    else:
        print("Login falhou.")


def menu_inicial(s):
    while True:
        print("\n1) Login\n2) Registo\n0) Sair")
        op = ler_opcao("> ", 0, 2)
        if op == 1:
            fazer_login(s)
        elif op == 2:
            print("Registo em construção")
        else:
            return

if __name__ == "__main__":
    s = ligar()
    menu_inicial(s)
    s.close()