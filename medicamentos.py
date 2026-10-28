from database import start_connection as ligar


def listar():
    conn = ligar()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM medicamentos")
    lista = cursor.fetchall()
    conn.close()
    return lista


def procurar(texto):
    conn = ligar()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM medicamentos WHERE nome LIKE %s", ("%" + texto + "%",))
    lista = cursor.fetchall()
    conn.close()
    return lista


def obter(id):
    conn = ligar()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM medicamentos WHERE id = %s", (id,))
    medicamento = cursor.fetchone()
    conn.close()
    return medicamento



def adicionar(nome, principio_ativo, dosagem, forma, categoria, preco, stock, receita, validade):
    conn = ligar()
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO medicamentos
            (nome, categoria, preco, stock, validade)
        VALUES (%s, %s, %s, %s, %s)
        """,
        (nome, categoria, preco, stock, validade)
    )

    conn.commit()
    conn.close()


def atualizar(id, novo_preco, novo_stock, nova_validade):
    conn = ligar()
    cursor = conn.cursor()

    cursor.execute(
        """
        UPDATE medicamentos
        SET preco = %s, stock = %s, validade = %s
        WHERE id = %s
        """,
        (novo_preco, novo_stock, nova_validade, id)
    )

    conn.commit()

    atualizado = cursor.rowcount > 0

    conn.close()

    return atualizado



def atualizar_stock(id, novo_stock):
    conn = ligar()
    cursor = conn.cursor()
    cursor.execute("UPDATE medicamentos SET stock = %s WHERE id = %s", (novo_stock, id))
    conn.commit()
    conn.close()


def remover(id):
    conn = ligar()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM medicamentos WHERE id = %s", (id,))
    removido = cursor.rowcount > 0

    conn.commit()
    conn.close()
    return removido