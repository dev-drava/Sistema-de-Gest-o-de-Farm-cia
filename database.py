import hashlib
import mysql.connector
from contextlib import contextmanager
from pathlib import Path

FICHEIRO_SQL = Path(__file__).parent / "farmacia.sql"


CONFIG = {
    "host": "gateway01.ap-southeast-1.prod.alicloud.tidbcloud.com",
    "user": "QseGRPMo1XqGtHz.root",
    "password": "v9Ut1oWS3QywXWeR",
    "database": "gestao_farmacia",
    "port": "4000"
}


@contextmanager
def obter_conexao():
    conn = mysql.connector.connect(**CONFIG)
    try:
        yield conn
    finally:
        conn.close()


def hash_senha(senha):
    return hashlib.sha256(senha.encode()).hexdigest()

def criar_tabelas():
    texto = FICHEIRO_SQL.read_text(encoding="utf-8")
    texto = "\n".join(l for l in texto.splitlines() if not l.strip().startswith("--"))

    with obter_conexao() as conn:
        cur = conn.cursor()
        for instrucao in texto.split(";"):
            if instrucao.strip():
                cur.execute(instrucao)
        conn.commit()

def consultar(sql, params=()):
    with obter_conexao() as conn:
        cur = conn.cursor(dictionary=True)
        cur.execute(sql, params)
        return cur.fetchall()


def executar(sql, params=()):
    with obter_conexao() as conn:
        try:
            cur = conn.cursor()
            cur.execute(sql, params)
            conn.commit()
            return cur.lastrowid
        except Exception:
            conn.rollback()
            raise


def contar_utilizadores():
    return consultar("SELECT COUNT(*) AS n FROM utilizador")[0]["n"]


def registar_utilizador(nome, senha, tipo):
    if consultar("SELECT id FROM utilizador WHERE nome=%s", (nome,)):
        return False
    executar(
        "INSERT INTO utilizador (nome, palavra_passe_hash, tipo) VALUES (%s, %s, %s)",
        (nome, hash_senha(senha), tipo),
    )
    return True


def autenticar(nome, senha):
    r = consultar(
        "SELECT id, nome, tipo, palavra_passe_hash FROM utilizador WHERE nome=%s AND palavra_passe_hash=%s",
        (nome, hash_senha(senha)),
    )
    return r[0] if r else None


def listar_medicamentos():
    return consultar("SELECT * FROM medicamentos WHERE ativo=1")


def pesquisar_medicamentos(termo):
    t = f"%{termo}%"
    return consultar(
        "SELECT * FROM medicamentos WHERE ativo=1 AND (nome LIKE %s OR categoria LIKE %s)",
        (t, t),
    )


def adicionar_medicamento(nome, categoria, preco, stock, validade):
    return executar(
        "INSERT INTO medicamentos (nome, categoria, preco, stock, validade) VALUES (%s,%s,%s,%s,%s)",
        (nome, categoria, preco, stock, validade),
    )


def atualizar_medicamento(id_med, preco, stock, validade):
    executar(
        "UPDATE medicamentos SET preco=%s, stock=%s, validade=%s WHERE id=%s",
        (preco, stock, validade, id_med),
    )


def remover_medicamento(id_med):
    executar("UPDATE medicamentos SET ativo=0 WHERE id=%s", (id_med,))


def repor_stock(id_med, quantidade):
    executar("UPDATE medicamentos SET stock = stock + %s WHERE id=%s", (quantidade, id_med))


def registar_venda(id_med, id_cliente, quantidade, id_farm=None, metodo="dinheiro"):
    if quantidade <= 0:
        return "QUANTIDADE_INVALIDA", False

    with obter_conexao() as conn:
        try:
            cur = conn.cursor(dictionary=True)
            cur.execute("SELECT preco, stock, stock_minimo FROM medicamentos WHERE id=%s AND ativo=1 FOR UPDATE", (id_med,))
            med = cur.fetchone()

            if not med:
                return "MEDICAMENTO_NAO_ENCONTRADO", False
            if med["stock"] < quantidade:
                return "STOCK_INSUFICIENTE", False

            total = med["preco"] * quantidade
            cur.execute(
                "INSERT INTO vendas (id_medicamento, id_cliente, id_farmaceutico, quantidade, total, metodo_pagamento) VALUES (%s,%s,%s,%s,%s,%s)",
                (id_med, id_cliente, id_farm, quantidade, total, metodo),
            )
            cur.execute("UPDATE medicamentos SET stock = stock - %s WHERE id=%s", (quantidade, id_med))
            conn.commit()

            return "COMPRA_CONFIRMADA", (med["stock"] - quantidade) <= med["stock_minimo"]
        except Exception:
            conn.rollback()
            raise


_SQL_HISTORICO = (
    "SELECT v.id, m.nome AS medicamento, v.quantidade, v.total, v.metodo_pagamento, v.data_venda "
    "FROM vendas v JOIN medicamentos m ON m.id = v.id_medicamento "
)


def historico_cliente(id_cliente):
    return consultar(_SQL_HISTORICO + "WHERE v.id_cliente=%s ORDER BY v.data_venda DESC", (id_cliente,))


def historico_farmaceutico(id_farm):
    return consultar(_SQL_HISTORICO + "WHERE v.id_farmaceutico=%s ORDER BY v.data_venda DESC", (id_farm,))


def historico_total():
    return consultar(_SQL_HISTORICO + "ORDER BY v.data_venda DESC")


if __name__ == "__main__":
    criar_tabelas()
    print("Utilizadores na BD:", contar_utilizadores())