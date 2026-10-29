
from datetime import date
from database import start_connection as ligar


def criar_tabelas():
    conn = ligar()
    cursor = conn.cursor()
    cursor.execute(
        "CREATE TABLE IF NOT EXISTS vendas ("
        "id INT AUTO_INCREMENT PRIMARY KEY, "
        "data_venda DATETIME DEFAULT CURRENT_TIMESTAMP, "
        "total DECIMAL(8,2) NOT NULL)"
    )
    cursor.execute(
        "CREATE TABLE IF NOT EXISTS itens_venda ("
        "id INT AUTO_INCREMENT PRIMARY KEY, "
        "id_venda INT NOT NULL, "
        "id_medicamento INT NOT NULL, "
        "quantidade INT NOT NULL, "
        "preco DECIMAL(6,2) NOT NULL)"
    )
    conn.commit()
    conn.close()


def verificar(medicamento, quantidade, tem_receita):
    if quantidade <= 0:
        return "Quantidade inválida."
    if medicamento["receita_obrigatoria"] and not tem_receita:
        return "Este medicamento precisa de receita."
    if medicamento["validade"] < date.today():
        return "Medicamento fora de validade."
    if quantidade > medicamento["stock"]:
        return "Stock insuficiente. Só há " + str(medicamento["stock"]) + "."


def adicionar_ao_carrinho(carrinho, medicamento, quantidade):
    for item in carrinho:
        if item["id"] == medicamento["id"]:
            item["quantidade"] += quantidade
            return

    carrinho.append({
        "id": medicamento["id"],
        "nome": medicamento["nome"],
        "preco": float(medicamento["preco"]),
        "quantidade": quantidade
    })


def calcular_total(carrinho):
    total = 0
    for item in carrinho:
        total += item["preco"] * item["quantidade"]
    return total


def finalizar_venda(carrinho, id_cliente=None):
    conn = ligar()
    cursor = conn.cursor()

    cursor.execute(
        "INSERT INTO vendas (total, id_cliente) VALUES (%s, %s)",
        (calcular_total(carrinho), id_cliente)
    )
    id_venda = cursor.lastrowid

    for item in carrinho:
        cursor.execute(
            "INSERT INTO itens_venda "
            "(id_venda, id_medicamento, quantidade, preco) "
            "VALUES (%s, %s, %s, %s)",
            (id_venda, item["id"], item["quantidade"], item["preco"])
        )
        cursor.execute(
            "UPDATE medicamentos SET stock = stock - %s WHERE id = %s",
            (item["quantidade"], item["id"])
        )

    conn.commit()
    conn.close()
    return id_venda


def listar_vendas():
    conn = ligar()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT
            v.id AS id_venda,
            v.id_cliente,
            v.id_farmaceutico,
            v.data_venda,
            v.total,
            iv.id_medicamento,
            m.nome AS medicamento,
            iv.quantidade,
            iv.preco
        FROM vendas v
        LEFT JOIN itens_venda iv ON iv.id_venda = v.id
        LEFT JOIN medicamentos m ON m.id = iv.id_medicamento
        ORDER BY v.id DESC
    """)
    lista = cursor.fetchall()
    conn.close()
    return lista
