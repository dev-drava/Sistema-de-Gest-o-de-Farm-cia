import socket
import json
import decimal
from autentificacao import criar_utilizador
import medicamentos as med_db
import vendas as venda_db

HOST = "0.0.0.0"
PORTA = 5000

# Codificador para lidar com objetos Decimal vindos da base de dados MySQL
class DecimalEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, decimal.Decimal):
            return float(obj)
        return super(DecimalEncoder, self).default(obj)

# Garante que as tabelas de vendas estão prontas
try:
    venda_db.criar_tabelas()
except Exception as e:
    print(f"Aviso ao criar tabelas de vendas: {e}")

def tratar_pedido(pedido, sessao_atual):
    acao = pedido.get("acao", "").upper()
    
    try:
        # ----------------------------------------------------
        # AUTENTICAÇÃO E REGISTO
        # ----------------------------------------------------
        if acao == "REGISTAR":
            from database import contar_utilizadores, registar_utilizador
            total_users = contar_utilizadores()
            tipo_pedido = pedido.get("tipo", "Cliente")
            
            # O primeiro utilizador é obrigatoriamente Admin
            if total_users == 0:
                tipo_final = "Admin"
            else:
                tipo_final = tipo_pedido

            sucesso = registar_utilizador(pedido.get("nome"), pedido.get("senha"), tipo_final)
            if sucesso:
                return {"resposta": "REGISTO_OK"}
            else:
                return {"resposta": "UTILIZADOR_EXISTE"}

        elif acao == "LOGIN":
            from database import autenticar
            nome = pedido.get("nome")
            senha = pedido.get("senha")
            
            user_db = autenticar(nome, senha)
            if not user_db:
                return {"resposta": "LOGIN_ERRO"}
            else:
                objeto_user = criar_utilizador(user_db["id"], user_db["nome"], user_db["palavra_passe_hash"], user_db["tipo"])
                sessao_atual["user"] = objeto_user
                return {
                    "resposta": "LOGIN_OK",
                    "tipo": objeto_user.tipo
                }

        # ----------------------------------------------------
        # MEDICAMENTOS (Listar e Pesquisar)
        # ----------------------------------------------------
        elif acao == "LISTAR":
            lista = med_db.listar()
            for m in lista:
                if "validade" in m and m["validade"]:
                    m["validade"] = str(m["validade"])
            return {"resposta": "OK", "dados": lista}

        elif acao == "PESQUISAR":
            termo = pedido.get("termo", "")
            lista = med_db.procurar(termo)
            for m in lista:
                if "validade" in m and m["validade"]:
                    m["validade"] = str(m["validade"])
            return {"resposta": "OK", "dados": lista}

        # ----------------------------------------------------
        # COMPRA / VENDA (Fluxo de Carrinho e Verificações)
        # ----------------------------------------------------
        elif acao == "VERIFICAR_ITEM":
            id_med = pedido.get("id_medicamento")
            quantidade = pedido.get("quantidade", 0)
            tem_receita = pedido.get("tem_receita", False)
            
            medicamento = med_db.obter(id_med)
            if not medicamento:
                return {"resposta": "ERRO", "mensagem": "Medicamento não encontrado."}
                
            erro_msg = venda_db.verificar(medicamento, quantidade, tem_receita)
            if erro_msg:
                return {"resposta": "FALHA_VERIFICACAO", "mensagem": erro_msg}
            return {"resposta": "VERIFICACAO_OK"}

        elif acao == "FINALIZAR_VENDA":
            carrinho = pedido.get("carrinho", [])
            if not carrinho:
                return {"resposta": "CARRINHO_VAZIO"}
                
            id_venda = venda_db.finalizar_venda(carrinho)
            return {"resposta": "VENDA_SUCESSO", "id_venda": id_venda}

        # ----------------------------------------------------
        # OPÇÕES DO FARMACÊUTICO / ADMIN
        # ----------------------------------------------------
        elif acao == "REPOR_STOCK":
            utilizador_atual = sessao_atual.get("user")
            if not utilizador_atual or utilizador_atual.tipo not in ["Admin", "Farmaceutico"]:
                return {"resposta": "PERMISSAO_NEGADA"}
                
            id_med = pedido.get("id_medicamento")
            novo_stock = pedido.get("novo_stock")
            
            med_db.atualizar_stock(id_med, novo_stock)
            return {"resposta": "STOCK_ATUALIZADO"}

        elif acao == "VER_HISTORICO_VENDAS":
            utilizador_atual = sessao_atual.get("user")
            if not utilizador_atual or utilizador_atual.tipo not in ["Admin", "Farmaceutico"]:
                return {"resposta": "PERMISSAO_NEGADA"}
                
            vendas = venda_db.listar_vendas()
            for v in vendas:
                if "data_venda" in v and v["data_venda"]:
                    v["data_venda"] = str(v["data_venda"])
            return {"resposta": "OK", "dados": vendas}

        return {"resposta": "ERRO_ACAO_DESCONHECIDA"}

    except Exception as e:
        print(f"Erro ao processar a ação '{acao}': {e}")
        return {"resposta": "ERRO_SERVIDOR", "detalhes": str(e)}


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
                pedido = json.loads(texto_recebido)
            except json.JSONDecodeError:
                resposta = {"resposta": "ERRO_JSON"}
                conexao.sendall((json.dumps(resposta) + "\n").encode("utf-8"))
                continue
                
            resposta = tratar_pedido(pedido, sessao_atual)
            
            # Envia sempre uma resposta formatada para o cliente não bloquear
            resposta_texto = json.dumps(resposta, cls=DecimalEncoder) + "\n"
            conexao.sendall(resposta_texto.encode("utf-8"))
            
    except Exception as erro:
        print(f"Erro na ligação com o cliente {endereco}: {erro}")
    finally:
        conexao.close()
        print(f"Cliente desconectado: {endereco}")


def iniciar_servidor():
    servidor = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    servidor.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    servidor.bind((HOST, PORTA))
    servidor.listen(5)
    print(f"Servidor da farmácia a funcionar na porta {PORTA}...")
    
    try:
        while True:
            conexao, endereco = servidor.accept()
            gerir_cliente(conexao, endereco)
    except KeyboardInterrupt:
        print("\nA desligar o servidor...")
    finally:
        servidor.close()


if __name__ == "__main__":
    iniciar_servidor()