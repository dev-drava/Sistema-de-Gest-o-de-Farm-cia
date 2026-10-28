
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
        return super(DecimalEncoder, self).default(obj)


try:
    venda_db.criar_tabelas()
except Exception as e:
    print(f"Aviso ao criar tabelas de vendas: {e}")


def tratar_pedido(pedido, sessao_atual):
    acao = pedido.get("acao", "").upper()

    try:
        # AUTENTICAÇÃO E REGISTO
        if acao == "REGISTAR":
            from database import contar_utilizadores, registar_utilizador

            total_users = contar_utilizadores()
            tipo_pedido = pedido.get("tipo", "Cliente")

            if total_users == 0:
                tipo_final = "Admin"
            else:
                tipo_final = tipo_pedido

            sucesso = registar_utilizador(
                pedido.get("nome"),
                pedido.get("senha"),
                tipo_final
            )

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
                return {"resposta": "LOGIN_INVALIDO"}

            objeto_user = criar_utilizador(
                user_db["id"],
                user_db["nome"],
                user_db["palavra_passe_hash"],
                user_db["tipo"]
            )

            sessao_atual["user"] = objeto_user

            return {
                "resposta": "LOGIN_OK",
                "tipo": objeto_user.tipo,
                "id": objeto_user.id
            }

        # MEDICAMENTOS: LISTAR E PESQUISAR
        elif acao == "LISTAR":
            lista = med_db.listar()

            for m in lista:
                if "validade" in m and m["validade"]:
                    m["validade"] = str(m["validade"])

            return {
                "resposta": "OK",
                "dados": lista
            }

        elif acao == "PESQUISAR":
            termo = pedido.get("termo", "")
            lista = med_db.procurar(termo)

            for m in lista:
                if "validade" in m and m["validade"]:
                    m["validade"] = str(m["validade"])

            return {
                "resposta": "OK",
                "dados": lista
            }

        # AÇÕES DE ADMIN
        # ADICIONAR MEDICAMENTO
        elif acao == "ADICIONAR_MED":
            utilizador_atual = sessao_atual.get("user")

            if not utilizador_atual or utilizador_atual.tipo != "Admin":
                return {"resposta": "PERMISSAO_NEGADA"}

            nome = pedido.get("nome")
            principio_ativo = pedido.get("principio_ativo")
            dosagem = pedido.get("dosagem")
            forma = pedido.get("forma")
            categoria = pedido.get("categoria")
            preco = pedido.get("preco")
            stock = pedido.get("stock")
            receita = pedido.get("receita", 0)
            validade = pedido.get("validade")

            med_db.adicionar(
                nome,
                principio_ativo,
                dosagem,
                forma,
                categoria,
                preco,
                stock,
                receita,
                validade
            )

            return {"resposta": "MEDICAMENTO_ADICIONADO"}

        # ATUALIZAR MEDICAMENTO
        elif acao == "ATUALIZAR_MED":
            utilizador_atual = sessao_atual.get("user")

            if not utilizador_atual or utilizador_atual.tipo != "Admin":
                return {"resposta": "PERMISSAO_NEGADA"}

            id_med = pedido.get("id_medicamento")
            preco = pedido.get("preco")
            stock = pedido.get("stock")
            validade = pedido.get("validade")

            med_db.atualizar(id_med, preco, stock, validade)

            return {"resposta": "MEDICAMENTO_ATUALIZADO"}

        # REMOVER MEDICAMENTO
        elif acao == "REMOVER_MED":
            utilizador_atual = sessao_atual.get("user")

            if not utilizador_atual or utilizador_atual.tipo != "Admin":
                return {"resposta": "PERMISSAO_NEGADA"}

            id_med = pedido.get("id_medicamento")

            if hasattr(med_db, "remover"):
                med_db.remover(id_med)
            elif hasattr(med_db, "apagar"):
                med_db.apagar(id_med)

            return {"resposta": "MEDICAMENTO_REMOVIDO"}

        # CRIAR FARMACÊUTICO
        elif acao == "CRIAR_FARMACEUTICO":
            utilizador_atual = sessao_atual.get("user")

            if not utilizador_atual or utilizador_atual.tipo != "Admin":
                return {"resposta": "PERMISSAO_NEGADA"}

            from database import registar_utilizador

            nome = pedido.get("nome")
            senha = pedido.get("senha")

            sucesso = registar_utilizador(
                nome,
                senha,
                "Farmaceutico"
            )

            if sucesso:
                return {"resposta": "REGISTO_OK"}

            return {"resposta": "UTILIZADOR_EXISTE"}

        # AÇÕES DE COMPRA, VENDA E REPOSIÇÃO DE STOCK
        elif acao == "COMPRAR":
            id_med = pedido.get("id_medicamento")
            quantidade = pedido.get("quantidade", 0)

            utilizador_atual = sessao_atual.get("user")
            id_cliente = utilizador_atual.id if utilizador_atual else None

            medicamento = med_db.obter(id_med)

            if not medicamento:
                return {"resposta": "MEDICAMENTO_NAO_ENCONTRADO"}

            carrinho = [{
                "id": medicamento["id"],
                "nome": medicamento["nome"],
                "preco": float(medicamento["preco"]),
                "quantidade": quantidade
            }]

            venda_db.finalizar_venda(
                carrinho,
                id_cliente=id_cliente
            )

            return {"resposta": "COMPRA_CONFIRMADA"}

        elif acao == "VENDER":
            utilizador_atual = sessao_atual.get("user")

            if (
                not utilizador_atual
                or utilizador_atual.tipo not in ["Admin", "Farmaceutico"]
            ):
                return {"resposta": "PERMISSAO_NEGADA"}

            id_med = pedido.get("id_medicamento")
            quantidade = pedido.get("quantidade", 0)
            id_cliente = pedido.get("id_cliente")

            medicamento = med_db.obter(id_med)

            if not medicamento:
                return {"resposta": "MEDICAMENTO_NAO_ENCONTRADO"}

            carrinho = [{
                "id": medicamento["id"],
                "nome": medicamento["nome"],
                "preco": float(medicamento["preco"]),
                "quantidade": quantidade
            }]

            venda_db.finalizar_venda(
                carrinho,
                id_cliente=id_cliente
            )

            return {"resposta": "VENDA_REGISTADA"}

        elif acao == "REPOR":
            utilizador_atual = sessao_atual.get("user")

            if (
                not utilizador_atual
                or utilizador_atual.tipo not in ["Admin", "Farmaceutico"]
            ):
                return {"resposta": "PERMISSAO_NEGADA"}

            id_med = pedido.get("id_medicamento")
            quantidade = pedido.get("quantidade", 0)

            med_db.atualizar_stock(id_med, quantidade)

            return {"resposta": "STOCK_REPOSTO"}

        # HISTÓRICOS
        elif acao == "HISTORICO":
            utilizador_atual = sessao_atual.get("user")

            if not utilizador_atual:
                return {"resposta": "PERMISSAO_NEGADA"}

            if utilizador_atual.tipo == "Cliente":
                if hasattr(venda_db, "listar_vendas_por_cliente"):
                    vendas = venda_db.listar_vendas_por_cliente(
                        utilizador_atual.id
                    )
                else:
                    vendas = []
            else:
                if hasattr(venda_db, "listar_vendas"):
                    vendas = venda_db.listar_vendas()
                else:
                    vendas = []

            for v in vendas:
                if "data_venda" in v and v["data_venda"]:
                    v["data_venda"] = str(v["data_venda"])

            return {
                "resposta": "OK",
                "dados": vendas
            }

        return {"resposta": "ERRO"}

    except Exception as e:
        print(f"Erro ao processar a ação '{acao}': {e}")

        return {
            "resposta": "ERRO",
            "detalhes": str(e)
        }


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
                resposta = {"resposta": "ERRO"}

                conexao.sendall(
                    (json.dumps(resposta) + "\n").encode("utf-8")
                )
                continue

            resposta = tratar_pedido(pedido, sessao_atual)

            resposta_texto = (
                json.dumps(resposta, cls=DecimalEncoder) + "\n"
            )

            conexao.sendall(resposta_texto.encode("utf-8"))

    except Exception as erro:
        print(f"Erro na ligação com o cliente {endereco}: {erro}")

    finally:
        conexao.close()
        print(f"Cliente desconectado: {endereco}")


def iniciar_servidor():
    servidor = socket.socket(
        socket.AF_INET,
        socket.SOCK_STREAM
    )

    servidor.setsockopt(
        socket.SOL_SOCKET,
        socket.SO_REUSEADDR,
        1
    )

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
