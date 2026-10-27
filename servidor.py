import json
import socket
import threading
import database as db
from autentificacao import criar_utilizador

HOST = "0.0.0.0"
PORT = 5000

TIPOS_UTILIZADOR = {
    "admin": "Admin", 
    "farmaceutico": "Farmaceutico", 
    "cliente": "Cliente"
}

def tem_permissao(utilizador, permissao):
    if utilizador is None:
        return False
    return utilizador.tem_permissao(permissao)


def tratar_pedido(pedido, sessao):
    acao = pedido.get("acao")
    utilizador_atual = sessao.get("user")

    if acao == "REGISTAR":
        total_users = db.contar_utilizadores()
        if total_users == 0:
            tipo = "admin"
        else:
            tipo = "cliente"
            
        sucesso = db.registar_utilizador(pedido["nome"], pedido["senha"], tipo)
        
        if sucesso:
            return {"resposta": "REGISTO_OK"}
        else:
            return {"resposta": "UTILIZADOR_EXISTE"}

    if acao == "LOGIN":
        user_db = db.autenticar(pedido["nome"], pedido["senha"])
        
        if not user_db:
            return {"resposta": "LOGIN_INVALIDO"}
        
        tipo_str = TIPOS_UTILIZADOR[user_db["tipo"]]
        objeto_user = criar_utilizador(user_db["id"], user_db["nome"], user_db["palavra_passe_hash"], tipo_str)
        
        sessao["user"] = objeto_user
        
        return {
            "resposta": "LOGIN_OK", 
            "tipo": objeto_user.tipo, 
            "id": objeto_user.id
        }

    if utilizador_atual is None:
        return {"resposta": "PERMISSAO_NEGADA"}

    if acao == "LISTAR":
        if tem_permissao(utilizador_atual, "listar_medicamentos") or tem_permissao(utilizador_atual, "consultar_stock"):
            medicamentos = db.listar_medicamentos()
            return {"resposta": "OK", "dados": medicamentos}

    elif acao == "COMPRAR":
        if tem_permissao(utilizador_atual, "efetuar_compra"):
            resultado, stock_baixo = db.registar_venda(
                pedido["id_medicamento"], 
                utilizador_atual.id, 
                pedido["quantidade"], 
                None, 
                pedido.get("metodo", "dinheiro")
            )
            
            resposta_cliente = {"resposta": resultado}
            if stock_baixo:
                resposta_cliente["alerta"] = "ALERTA_STOCK_BAIXO"
                
            return resposta_cliente

    elif acao == "ADICIONAR_MED":
        if tem_permissao(utilizador_atual, "adicionar_medicamento"):
            db.adicionar_medicamento(
                pedido["nome"], 
                pedido.get("categoria"), 
                pedido["preco"], 
                pedido["stock"], 
                pedido.get("validade")
            )
            return {"resposta": "MEDICAMENTO_ADICIONADO"}

    return {"resposta": "PERMISSAO_NEGADA"}


def gerir_cliente(conexao, endereco):
    print(f"Novo cliente ligado: {endereco}")
    sessao_atual = {}
    
    try:
        while True:
            dados = conexao.recv(4096)
            if not dados:
                break
                
            texto_recebido = dados.decode("utf-8").strip()
            if not texto_recebido:
                continue
                
            try:
                pedido_json = json.loads(texto_recebido)
            except json.JSONDecodeError:
                print(f"[AVISO] Dados inválidos recebidos de {endereco} (não é JSON).")
                continue
            
            resposta = tratar_pedido(pedido_json, sessao_atual)
            
            resposta_json = json.dumps(resposta, default=str) + "\n"
            conexao.sendall(resposta_json.encode("utf-8"))
            
    except Exception as erro:
        print(f"Aconteceu um erro com o cliente {endereco}: {erro}")


def main():
    servidor = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    servidor.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    servidor.bind((HOST, PORT))
    servidor.listen()
    
    print(f"Servidor da farmácia a funcionar na porta {PORT}...")
    
    try:
        while True:
            conexao, endereco = servidor.accept()
            thread_cliente = threading.Thread(target=gerir_cliente, args=(conexao, endereco))
            thread_cliente.start()
    except KeyboardInterrupt:
        print("\nA desligar o servidor...")
    finally:
        servidor.close()


if __name__ == "__main__":
    main()