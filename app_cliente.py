import socket
import json

HOST = "127.0.0.1"
PORTA = 5000

def ligar():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((HOST, PORTA))
    return s

def pedir(s, pedido_dict):
    mensagem = json.dumps(pedido_dict) + "\n"
    s.sendall(mensagem.encode("utf-8"))
    
    dados = s.recv(4096)
    if not dados:
        return {"resposta": "ERRO"}
        
    try:
        return json.loads(dados.decode("utf-8").strip())
    except json.JSONDecodeError:
        return {"resposta": "ERRO"}


def ler_opcao(prompt, minimo, maximo):
    while True:
        texto = input(prompt).strip()
        if texto.isdigit() and minimo <= int(texto) <= maximo:
            return int(texto)
        print("Opção inválida.")

def ler_texto(prompt):
    while True:
        texto = input(prompt).strip()
        if texto:
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
    "LOGIN_INVALIDO": "Credenciais inválidas.",
    "REGISTO_OK": "Registo concluído. Já podes fazer login.",
    "UTILIZADOR_EXISTE": "Não foi possível registar (o utilizador já existe?).",
    "COMPRA_CONFIRMADA": "Compra efetuada com sucesso.",
    "STOCK_INSUFICIENTE": "Não há stock suficiente.",
    "VENDA_REGISTADA": "Venda registada com sucesso.",
    "STOCK_REPOSTO": "Stock reposto com sucesso.",
    "MEDICAMENTO_ADICIONADO": "Medicamento adicionado.",
    "MEDICAMENTO_ATUALIZADO": "Medicamento atualizado.",
    "MEDICAMENTO_REMOVIDO": "Medicamento removido.",
    "MEDICAMENTO_NAO_ENCONTRADO": "Medicamento não encontrado.",
    "PERMISSAO_NEGADA": "Não tens permissão para esta operação.",
}

def mostrar(resp_dict):
    codigo = resp_dict.get("resposta", "ERRO").upper()

    print(MENSAGENS.get(
        codigo,
        "Resposta do servidor: " + str(resp_dict)
    ))

    if resp_dict.get("detalhes"):
        print("Detalhes do erro:", resp_dict["detalhes"])

    if "alerta" in resp_dict:
        print("ALERTA: Stock do medicamento ficou abaixo do mínimo!")

def mostrar_lista(resp_dict):
    if resp_dict.get("resposta") != "OK":
        mostrar(resp_dict)
        return
    
    dados = resp_dict.get("dados", [])
    if not dados:
        print("\nNão existem registos.")
        return
        
    print()
    for item in dados:
        detalhes = " | ".join(f"{k}: {v}" for k, v in item.items())
        print(f" - {detalhes}")


def menu_cliente(s):
    while True:
        print("\nCLIENTE")
        print("1) Listar medicamentos")
        print("2) Pesquisar medicamentos")
        print("3) Efetuar compra")
        print("4) Ver o meu histórico")
        print("0) Sair")
        op = ler_opcao("> ", 0, 4)
        
        if op == 1:
            mostrar_lista(pedir(s, {"acao": "LISTAR"}))
        elif op == 2:
            termo = ler_texto("Termo a pesquisar: ")
            mostrar_lista(pedir(s, {"acao": "PESQUISAR", "termo": termo}))
        elif op == 3:
            id_med = ler_opcao("ID do medicamento: ", 0, 999999)
            qtd = ler_opcao("Quantidade: ", 0, 999999)
            mostrar(pedir(s, {"acao": "COMPRAR", "id_medicamento": id_med, "quantidade": qtd}))
        elif op == 4:
            mostrar_lista(pedir(s, {"acao": "HISTORICO"}))
        else:
            return


def menu_farmaceutico(s):
    while True:
        print("\n FARMACÊUTICO")
        print("1. Listar medicamentos")
        print("2. Registar venda")
        print("3. Repor stock")
        print("4) Ver as minhas vendas")
        print("0) Sair")
        op = ler_opcao("> ", 0, 4)
        
        if op == 1:
            mostrar_lista(pedir(s, {"acao": "LISTAR"}))
        elif op == 2:
            id_cli = ler_opcao("ID do cliente: ", 0, 9999999)
            id_med = ler_opcao("ID do medicamento: ", 0, 999999)
            qtd = ler_opcao("Quantidade: ", 0, 999999)
            mostrar(pedir(s, {"acao": "VENDER", "id_cliente": id_cli, "id_medicamento": id_med, "quantidade": qtd}))
        elif op == 3:
            id_med = ler_opcao("ID do medicamento: ", 0, 999999)
            qtd = ler_opcao("Quantidade a repor: ", 0, 9999999)
            mostrar(pedir(s, {"acao": "REPOR", "id_medicamento": id_med, "quantidade": qtd}))
        elif op == 4:
            mostrar_lista(pedir(s, {"acao": "HISTORICO"}))
        else:
            return


def menu_admin(s):
    while True:
        print("\nADMIN")
        print("1) Adicionar medicamento")
        print("2) Atualizar medicamento")
        print("3) Remover medicamento")
        print("4) Listar medicamentos")
        print("5) Criar farmacêutico")
        print("6) Ver histórico total")
        print("0) Logout")
        op = ler_opcao("> ", 0, 6)
        
        if op == 1:
            nome = ler_texto("Nome: ")
            cat = ler_texto("Categoria: ")
            preco = ler_preco("Preço: ")
            stock = ler_opcao("Stock inicial: ", 0, 999999)
            validade = ler_texto("Validade (AAAA-MM-DD): ")
            mostrar(pedir(s, {"acao": "ADICIONAR_MED", "nome": nome, "categoria": cat, "preco": preco, "stock": stock, "validade": validade}))
        elif op == 2:
            id_med = ler_opcao("ID do medicamento: ", 1, 999999)
            preco = ler_preco("Novo preço: ")
            stock = ler_opcao("Novo stock: ", 0, 999999)
            validade = ler_texto("Nova validade (AAAA-MM-DD): ")
            mostrar(pedir(s, {"acao": "ATUALIZAR_MED", "id_medicamento": id_med, "preco": preco, "stock": stock, "validade": validade}))
        elif op == 3:
            id_med = ler_opcao("ID do medicamento: ", 0, 999999)
            mostrar(pedir(s, {"acao": "REMOVER_MED", "id_medicamento": id_med}))
        elif op == 4:
            mostrar_lista(pedir(s, {"acao": "LISTAR"}))
        elif op == 5:
            nome = ler_texto("Nome do farmacêutico: ")
            senha = ler_texto("Palavra-passe: ")
            mostrar(pedir(s, {"acao": "CRIAR_FARMACEUTICO", "nome": nome, "senha": senha}))
        elif op == 6:
            mostrar_lista(pedir(s, {"acao": "HISTORICO"}))
        else:
            return


MENUS = {
    "ADMIN": menu_admin,
    "FARMACEUTICO": menu_farmaceutico,
    "CLIENTE": menu_cliente,
}

def fazer_login(s):
    nome = ler_texto("Utilizador: ")
    senha = ler_texto("Palavra-passe: ")
    resp = pedir(s, {"acao": "LOGIN", "nome": nome, "senha": senha})
    
    if resp.get("resposta") == "LOGIN_OK":
        tipo = resp.get("tipo", "").upper()
        menu = MENUS.get(tipo)
        if menu:
            menu(s)
        else:
            print("Tipo de utilizador desconhecido:", tipo)
    else:
        mostrar(resp)


def fazer_registo(s):
    print("\nTIPO DE CONTA:")
    print("1) Cliente")
    print("2) Farmacêutico")
    op_tipo = ler_opcao("> ", 1, 2)
    
    tipo_escolhido = "Cliente" if op_tipo == 1 else "Farmaceutico"

    nome = ler_texto("Novo utilizador: ")
    senha = ler_texto("Palavra-passe: ")
    
    mostrar(pedir(s, {"acao": "REGISTAR", "nome": nome, "senha": senha, "tipo": tipo_escolhido}))


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