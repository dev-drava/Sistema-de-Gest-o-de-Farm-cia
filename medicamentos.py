from database import ligar


def _executar(sql, params=(), fetch=None):
    conn = ligar()
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute(sql, params)
        if fetch == "all":
            return cursor.fetchall()
        if fetch == "one":
            return cursor.fetchone()
        conn.commit()
    finally:
        conn.close()


def listar():
    return _executar("SELECT * FROM medicamentos", fetch="all")


def procurar(texto):
    return _executar(
        "SELECT * FROM medicamentos WHERE nome LIKE %s",
        (f"%{texto}%",),
        fetch="all",
    )


def obter(id):
    return _executar("SELECT * FROM medicamentos WHERE id = %s", (id,), fetch="one")


def adicionar(nome, principio_ativo, dosagem, forma, categoria, preco, stock, receita, validade):
    _executar(
        "INSERT INTO medicamentos (nome, principio_ativo, dosagem, forma, categoria, preco, stock, receita_obrigatoria, validade) "
        "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)",
        (nome, principio_ativo, dosagem, forma, categoria, preco, stock, receita, validade),
    )
    conn.commit()
    conn.close()


def atualizar_stock(id, novo_stock):
    _executar("UPDATE medicamentos SET stock = %s WHERE id = %s", (novo_stock, id))


def remover(id):
    _executar("DELETE FROM medicamentos WHERE id = %s", (id,))