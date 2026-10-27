import json
import socket
import threading
import database as db
from autentificacao import criar_utilizador

HOST = "0.0.0.0"
PORT = 5000
TIPOS = {"admin": "Admin", "farmaceutico": "Farmaceutico", "cliente": "Cliente"}


def pode(user, *permissoes):
    """Verifica se o utilizador tem permissão para realizar uma ação."""
    return user is not None and any(user.tem_permissao(p) for p in permissoes)


def tratar_pedido(p, sessao):
    acao = p.get("acao")
    user = sessao.get("user")

    # 1. Ações públicas (não precisam de login prévio)
    if acao == "REGISTAR":
        # Se for o primeiro utilizador, cria como admin, senão como cliente
        tipo = "admin" if db.contar_utilizadores() == 0 else "cliente"
        ok = db.registar_utilizador(p["nome"], p["senha"], tipo)
        return {"resposta": "REGISTO_OK" if ok else "UTILIZADOR_EXISTE"}

    if acao == "LOGIN":
        u = db.autenticar(p["nome"], p["senha"])
        if not u:
            return {"resposta": "LOGIN_INVALIDO"}
        
        # Cria o objeto de utilizador (Herança - vindo da parte do teu amigo)
        obj = criar_utilizador(u["id"], u["nome"], u["palavra_passe_hash"], TIPOS[u["tipo"]])
        sessao["user"] = obj
        return {"resposta": "LOGIN_OK", "tipo": obj.tipo, "id": obj.id}

    # Se a ação exigir login e o utilizador não estiver autenticado
    if user is None:
        return {"resposta": "PERMISSAO_NEGADA"}

    # 2. Ações protegidas (verificam permissões)
    if acao == "LISTAR":
        if pode(user, "listar_medicamentos", "consultar_stock", "ver_stock"):
            return {"resposta": "OK", "dados": db.listar_medicamentos()}

    elif acao == "PESQUISAR":
        if pode(user, "pesquisar_medicamentos"):
            return {"resposta": "OK", "dados": db.pesquisar_medicamentos(p["termo"])}

    elif acao == "COMPRAR":
        if pode(user, "efetuar_compra"):
            res, baixo = db.registar_venda(p["id_medicamento"], user.id, p["quantidade"], None, p.get("metodo", "dinheiro"))
            resposta = {"resposta": res}
            if baixo:
                resposta["alerta"] = "ALERTA_STOCK_BAIXO"
            return resposta

    elif acao == "VENDER":
        if pode(user, "registar_venda"):
            res, baixo = db.registar_venda(p["id_medicamento"], p["id_cliente"], p["quantidade"], user.id, p.get("metodo", "dinheiro"))
            resposta = {"resposta": res}
            if baixo:
                resposta["alerta"] = "ALERTA_STOCK_BAIXO"
            return resposta

    elif acao == "REPOR":
        if pode(user, "repor_stock"):
            db.repor_stock(p["id_medicamento"], p["quantidade"])
            return {"resposta": "STOCK_REPOSTO"}

    elif acao == "ADICIONAR_MED":
        if pode(user, "adicionar_medicamento"):
            db.adicionar_medicamento(p["nome"], p.get("categoria"), p["preco"], p["stock"], p.get("validade"))
            return {"resposta": "MEDICAMENTO_ADICIONADO"}

    elif acao == "ATUALIZAR_MED":
        if pode(user, "atualizar_medicamento"):
            db.atualizar_medicamento(p["id_medicamento"], p["preco"], p["stock"], p.get("validade"))
            return {"resposta": "MEDICAMENTO_ATUALIZADO"}

    elif acao == "REMOVER_MED":
        if pode(user, "remover_medicamento"):
            db.remover_medicamento(p["id_medicamento"])
            return {"resposta": "MEDICAMENTO_REMOVIDO"}

    elif acao == "CRIAR_FARMACEUTICO":
        if pode(user, "criar_farmaceutico"):
            ok = db.registar_utilizador(p["nome"], p["senha"], "farmaceutico")
            return {"resposta": "REGISTO_OK" if ok else "UTILIZADOR_EXISTE"}

    elif acao == "HISTORICO":
        if pode(user, "ver_historico_total"):
            return {"resposta": "OK", "dados": db.historico_total()}
        elif pode(user, "ver_vendas_proprias"):
            return {"resposta": "OK", "dados": db.historico_farmaceutico(user.id)}
        elif pode(user, "ver_historico_proprio"):
            return {"resposta": "OK", "dados": db.historico_cliente(user.id)}

    return {"resposta": "PERMISSAO_NEGADA"}


def atender_cliente(conn, addr):
    print(f"Cliente ligado a partir de: {addr}")
    sessao = {}
    try:
        while True:
            dados = conn.recv(4096)
            if not dados:
                break
            
            mensagem = dados.decode("utf-8").strip()
            if not mensagem:
                continue
                
            pedido = json.loads(mensagem)
            resposta = tratar_pedido(pedido, sessao)
            
            conn.sendall((json.dumps(resposta, default=str) + "\n").encode("utf-8"))
            
    except Exception as e:
        print(f"Erro com o cliente {addr}: {e}")
    finally:
        conn.close()
        print(f"Cliente desligado: {addr}")


def main():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind((HOST, PORT))
    s.listen()
    
    print(f"Servidor à escuta na porta {PORT}...")
    
    try:
        while True:
            conn, addr = s.accept()
            t = threading.Thread(target=atender_cliente, args=(conn, addr), daemon=True)
            t.start()
    except KeyboardInterrupt:
        print("\nA encerrar o servidor...")
    finally:
        s.close()


if __name__ == "__main__":
    main()