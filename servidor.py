
import socket
import json
import decimal
from autentificacao import criar_utilizador
import medicamentos as med_db
import vendas as venda_db

HOST = "0.0.0.0"
PORTA = 5000


class DecimalEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, decimal.Decimal):
            return float(obj)
        return super().default(obj)


try:
    venda_db.criar_tabelas()
except Exception as e:
    print(f"Aviso ao criar tabelas de vendas: {e}")


def tratar_pedido(pedido, sessao_atual):
    acao = pedido.get("acao", "").upper()

    try:
        if acao == "REGISTAR":
            from database import contar_utilizadores, registar_utilizador

            total = contar_utilizadores()
            tipo = pedido.get("tipo", "Cliente")
            tipo = "Admin" if total == 0 else tipo

            sucesso = registar_utilizador(
                pedido.get("nome"),
                pedido.get("senha"),
                tipo
            )

            return {"resposta": "REGISTO_OK" if sucesso else "UTILIZADOR_EXISTE"}

        elif acao == "LOGIN":
            from database import autenticar

            user_db = autenticar(
                pedido.get("nome"),
                pedido.get("senha")
            )

            if not user_db:
                return {"resposta": "LOGIN_INVALIDO"}

            utilizador = criar_utilizador(
                user_db["id"],
                user_db["nome"],
                user_db["palavra_passe_hash"],
                user_db["tipo"]
            )

            sessao_atual["user"] = utilizador

            return {
                "resposta": "LOGIN_OK",
                "tipo": utilizador.tipo,
                "id": utilizador.id
            }

        elif acao == "LISTAR":
            lista = med_db.listar()

            for m in lista:
                if m.get("validade"):
                    m["validade"] = str(m["validade"])

            return {"resposta": "OK", "dados": lista}

        elif acao == "PESQUISAR":
            lista = med_db.procurar(pedido.get("termo", ""))

            for m in lista:
                if m.get("validade"):
                    m["validade"] = str(m["validade"])

            return {"resposta": "OK", "dados": lista}

        elif acao == "ADICIONAR_MED":
            utilizador = sessao_atual.get("user")

            if not utilizador or utilizador.tipo != "Admin":
                return {"resposta": "PERMISSAO_NEGADA"}

            med_db.adicionar(
                pedido.get("nome"),
                pedido.get("principio_ativo"),
                pedido.get("dosagem"),
                pedido.get("forma"),
                pedido.get("categoria"),
                pedido.get("preco"),
                pedido.get("stock"),
                pedido.get("receita", 0),
                pedido.get("validade")
            )

            return {"resposta": "MEDICAMENTO_ADICIONADO"}

        elif acao == "ATUALIZAR_MED":
            utilizador = sessao_atual.get("user")

            if not utilizador or utilizador.tipo != "Admin":
                return {"resposta": "PERMISSAO_NEGADA"}

            med_db.atualizar(
                pedido.get("id_medicamento"),
                pedido.get("preco"),
                pedido.get("stock"),
                pedido.get("validade")
            )

            return {"resposta": "MEDICAMENTO_ATUALIZADO"}

        elif acao == "REMOVER_MED":
            utilizador = sessao_atual.get("user")

            if not utilizador or utilizador.tipo != "Admin":
                return {"resposta": "PERMISSAO_NEGADA"}

            if hasattr(med_db, "remover"):
                med_db.remover(pedido.get("id_medicamento"))
            elif hasattr(med_db, "apagar"):
                med_db.apagar(pedido.get("id_medicamento"))

            return {"resposta": "MEDICAMENTO_REMOVIDO"}

        elif acao == "CRIAR_FARMACEUTICO":
            utilizador = sessao_atual.get("user")

            if not utilizador or utilizador.tipo != "Admin":
                return {"resposta": "PERMISSAO_NEGADA"}

            from database import registar_utilizador

            sucesso = registar_utilizador(
                pedido.get("nome"),
                pedido.get("senha"),
                "Farmaceutico"
            )

            return {"resposta": "REGISTO_OK" if sucesso else "UTILIZADOR_EXISTE"}

        elif acao in ["COMPRAR", "VENDER"]:
            utilizador = sessao_atual.get("user")

            if not utilizador:
                return {"resposta": "PERMISSAO_NEGADA"}

            if acao == "VENDER" and utilizador.tipo not in ["Admin", "Farmaceutico"]:
                return {"resposta": "PERMISSAO_NEGADA"}

            id_med = pedido.get("id_medicamento")
            quantidade = pedido.get("quantidade", 0)
            id_cliente = utilizador.id if acao == "COMPRAR" else pedido.get("id_cliente")

            if quantidade <= 0:
                return {"resposta": "QUANTIDADE_INVALIDA"}

            medicamento = med_db.obter(id_med)

            if not medicamento:
                return {"resposta": "MEDICAMENTO_NAO_ENCONTRADO"}

            if quantidade > medicamento["stock"]:
                return {"resposta": "STOCK_INSUFICIENTE"}

            carrinho = [{
                "id": medicamento["id"],
                "nome": medicamento["nome"],
                "preco": float(medicamento["preco"]),
                "quantidade": quantidade
            }]

            venda_db.finalizar_venda(carrinho, id_cliente=id_cliente)

            resposta = "COMPRA_CONFIRMADA" if acao == "COMPRAR" else "VENDA_REGISTADA"
            return {"resposta": resposta}

        elif acao == "REPOR":
            utilizador = sessao_atual.get("user")

            if not utilizador or utilizador.tipo not in ["Admin", "Farmaceutico"]:
                return {"resposta": "PERMISSAO_NEGADA"}

            quantidade = pedido.get("quantidade", 0)

            if quantidade <= 0:
                return {"resposta": "QUANTIDADE_INVALIDA"}

            med_db.atualizar_stock(
                pedido.get("id_medicamento"),
                quantidade
            )

            return {"resposta": "STOCK_REPOSTO"}

        elif acao == "HISTORICO":
            utilizador = sessao_atual.get("user")

            if not utilizador:
                return {"resposta": "PERMISSAO_NEGADA"}

            if utilizador.tipo == "Cliente":
                vendas = venda_db.listar_vendas_por_cliente(utilizador.id)
            else:
                vendas = venda_db.listar_vendas()

            for venda in vendas:
                if venda.get("data_venda"):
                    venda["data_venda"] = str(venda["data_venda"])

            return {"resposta": "OK", "dados": vendas}

        return {"resposta": "ERRO"}

    except Exception as e:
        print(f"Erro ao processar a ação '{acao}': {e}")
        return {"resposta": "ERRO", "detalhes": str(e)}


def gerir_cliente(conexao, endereco):
    print(f"Novo cliente ligado: {endereco}")
    sessao_atual = {}

    try:
        while True:
            dados = conexao.recv(4096)

            if not dados:
                break

            texto = dados.decode("utf-8").strip()

            if not texto:
                continue

            try:
                pedido = json.loads(texto)
            except json.JSONDecodeError:
                resposta = {"resposta": "ERRO"}
            else:
                resposta = tratar_pedido(pedido, sessao_atual)

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
