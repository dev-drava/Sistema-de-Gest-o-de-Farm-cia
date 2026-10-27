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
    resposta = s.recv(4096).decode().strip()
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

def ler_preco(prompt):

    while True:
        texto = input(prompt).strip().replace(",", ".")
        try:
            valor = float(texto)
            if valor > 0:
                return valor
        except ValueError:
            pass
        print("Preço inválido.")


MENSAGENS = {
    "OK": "Operação concluída com sucesso.",
    "ERRO": "Ocorreu um erro no servidor.",
    "LOGIN_OK": "Login efetuado.",
    "LOGIN_ERRO": "Credenciais inválidas.",
    "LOGIN_INVALIDO": "Credenciais inválidas.",
    "REGISTO_OK": "Registo concluído. Já podes fazer login.",
    "REGISTO_ERRO": "Não foi possível registar (o utilizador já existe?).",
    "COMPRA_CONFIRMADA": "Compra efetuada com sucesso.",
    "STOCK_INSUFICIENTE": "Não há stock suficiente.",
    "VENDA_REGISTADA": "Venda registada com sucesso.",
    "STOCK_REPOSTO": "Stock reposto com sucesso.",
    "MEDICAMENTO_ADICIONADO": "Medicamento adicionado.",
    "MEDICAMENTO_ATUALIZADO": "Medicamento atualizado.",
    "MEDICAMENTO_REMOVIDO": "Medicamento removido.",
    "MEDICAMENTO_NAO_ENCONTRADO": "Medicamento não encontrado.",
    "FARMACEUTICO_CRIADO": "Farmacêutico criado.",
    "PERMISSAO_NEGADA": "Não tens permissão para esta operação.",
    "SEM_PERMISSAO": "Não tens permissão para esta operação.",
}

def mostrar(resp):
    codigo = resp[0].upper()
    print(MENSAGENS.get(codigo, "Resposta do servidor: " + "|".join(resp)))

def mostrar_lista(resp):
    if resp[0].upper() != "OK" or len(resp) < 2 or not resp[1]:
        mostrar(resp)
        return
    print()
    for item in resp[1].split(";"):
        print(" - " + item.replace(",", " | "))



def menu_cliente(s):
    while True:
        print("\n--- CLIENTE ---")
        print("1) Listar medicamentos")
        print("2) Pesquisar medicamentos")
        print("3) Efetuar compra")
        print("4) Ver o meu histórico")
        print("0) Logout")
        op = ler_opcao("> ", 0, 4)
        if op == 1:
            mostrar_lista(pedir(s, "LISTAR_MEDICAMENTOS"))
        elif op == 2:
            nome = ler_texto("Nome a pesquisar: ")
            mostrar_lista(pedir(s, "PESQUISAR_MEDICAMENTOS", nome))
        elif op == 3:
            id_med = ler_opcao("ID do medicamento: ", 1, 9999)
            qtd = ler_opcao("Quantidade: ", 1, 9999)
            mostrar(pedir(s, "COMPRAR", id_med, qtd))
        elif op == 4:
            mostrar_lista(pedir(s, "VER_HISTORICO"))
        else:
            return


def menu_farmaceutico(s):
    while True:
        print("\n FARMACÊUTICO")
        print("1) Listar medicamentos")
        print("2) Ver stock")
        print("3) Registar venda")
        print("4) Repor stock")
        print("5) Ver as minhas vendas")
        print("0) Logout")
        op = ler_opcao("> ", 0, 5)
        if op == 1:
            mostrar_lista(pedir(s, "LISTAR_MEDICAMENTOS"))
        elif op == 2:
            mostrar_lista(pedir(s, "VER_STOCK"))
        elif op == 3:
            id_cliente = ler_opcao("ID do cliente: ", 1, 99999)
            id_med = ler_opcao("ID do medicamento: ", 1, 9999)
            qtd = ler_opcao("Quantidade: ", 1, 9999)
            mostrar(pedir(s, "REGISTAR_VENDA", id_cliente, id_med, qtd))
        elif op == 4:
            id_med = ler_opcao("ID do medicamento: ", 1, 9999)
            qtd = ler_opcao("Quantidade a repor: ", 1, 99999)
            mostrar(pedir(s, "REPOR_STOCK", id_med, qtd))
        elif op == 5:
            mostrar_lista(pedir(s, "VER_VENDAS_PROPRIAS"))
        else:
            return


def menu_admin(s):
    while True:
        print("\nADMIN")
        print("1) Adicionar medicamento")
        print("2) Atualizar medicamento")
        print("3) Remover medicamento")
        print("4) Consultar stock")
        print("5) Criar farmacêutico")
        print("0) Logout")
        op = ler_opcao("> ", 0, 5)
        if op == 1:
            nome = ler_texto("Nome: ")
            preco = ler_preco("Preço: ")
            stock = ler_opcao("Stock inicial: ", 0, 99999)
            mostrar(pedir(s, "ADICIONAR_MEDICAMENTO", nome, preco, stock))
        elif op == 2:
            id_med = ler_opcao("ID do medicamento: ", 1, 9999)
            preco = ler_preco("Novo preço: ")
            mostrar(pedir(s, "ATUALIZAR_MEDICAMENTO", id_med, preco))
        elif op == 3:
            id_med = ler_opcao("ID do medicamento: ", 1, 9999)
            mostrar(pedir(s, "REMOVER_MEDICAMENTO", id_med))
        elif op == 4:
            mostrar_lista(pedir(s, "CONSULTAR_STOCK"))
        elif op == 5:
            nome = ler_texto("Nome do farmacêutico: ")
            palavra_passe = ler_texto("Palavra-passe: ")
            mostrar(pedir(s, "CRIAR_FARMACEUTICO", nome, palavra_passe))
        else:
            return


MENUS = {
    "ADMIN": menu_admin,
    "ADMINISTRADOR": menu_admin,
    "FARMACEUTICO": menu_farmaceutico,
    "CLIENTE": menu_cliente,
}

def fazer_login(s):
    nome = ler_texto("Utilizador: ")
    palavra_passe = ler_texto("Palavra-passe: ")
    resp = pedir(s, "LOGIN", nome, palavra_passe)
    if resp[0].upper() == "LOGIN_OK" and len(resp) > 1:
        papel = resp[1].upper()
        menu = MENUS.get(papel)
        if menu is None:
            print("Papel desconhecido:", papel)
        else:
            menu(s)
    else:
        mostrar(resp)


def fazer_registo(s):
    nome = ler_texto("Novo utilizador: ")
    palavra_passe = ler_texto("Palavra-passe: ")
    mostrar(pedir(s, "REGISTO", nome, palavra_passe))


def menu_inicial(s):
    while True:
        print("\nFARMÁCIA")
        print("1) Login")
        print("2) Registo")
        print("0) Sair")
        op = ler_opcao("> ", 0, 2)
        if op == 1:
            fazer_login(s)
        elif op == 2:
            fazer_registo(s)
        else:
            return


if __name__ == "__main__":
    s = ligar()
    menu_inicial(s)
    s.close()