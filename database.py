import hashlib
from connect_db import start_connection

def encriptar_senha(senha):
    return hashlib.sha256(senha.encode()).hexdigest()


def contar_utilizadores():
    db = start_connection()
    cursor = db.cursor(dictionary=True)
    
    cursor.execute("SELECT COUNT(*) AS total FROM utilizador")
    resultado = cursor.fetchone()
    
    cursor.close()
    db.close()
    return resultado["total"]


def registar_utilizador(nome, senha, tipo):
    db = start_connection()
    cursor = db.cursor()
    
    cursor.execute("SELECT id FROM utilizador WHERE nome = %s", (nome,))
    existe = cursor.fetchone()
    
    if existe:
        cursor.close()
        db.close()
        return False
        
    senha_criptografada = encriptar_senha(senha)
    
    cursor.execute(
        "INSERT INTO utilizador (nome, palavra_passe_hash, tipo) VALUES (%s, %s, %s)",
        (nome, senha_criptografada, tipo)
    )
    db.commit()
    
    cursor.close()
    db.close()
    return True


def autenticar(nome, senha):
    db = start_connection()
    cursor = db.cursor(dictionary=True)
    
    senha_criptografada = encriptar_senha(senha)
    
    cursor.execute(
        "SELECT id, nome, tipo, palavra_passe_hash FROM utilizador WHERE nome = %s AND palavra_passe_hash = %s",
        (nome, senha_criptografada)
    )
    utilizador = cursor.fetchone()
    
    cursor.close()
    db.close()
    return utilizador


def listar_medicamentos():
    db = start_connection()
    cursor = db.cursor(dictionary=True)
    
    cursor.execute("SELECT * FROM medicamentos WHERE ativo = 1")
    lista = cursor.fetchall()
    
    cursor.close()
    db.close()
    return lista


def adicionar_medicamento(nome, categoria, preco, stock, validade):
    db = start_connection()
    cursor = db.cursor()
    
    cursor.execute(
        "INSERT INTO medicamentos (nome, categoria, preco, stock, validade) VALUES (%s, %s, %s, %s, %s)",
        (nome, categoria, preco, stock, validade)
    )
    db.commit()
    
    cursor.close()
    db.close()


def registar_venda(id_med, id_cliente, quantidade, id_farmaceutico=None, metodo="dinheiro"):
    if quantidade <= 0:
        return "QUANTIDADE_INVALIDA", False

    db = start_connection()
    cursor = db.cursor(dictionary=True)
    
    cursor.execute("SELECT preco, stock, stock_minimo FROM medicamentos WHERE id = %s AND ativo = 1", (id_med,))
    med = cursor.fetchone()

    if not med:
        cursor.close()
        db.close()
        return "MEDICAMENTO_NAO_ENCONTRADO", False
        
    if med["stock"] < quantidade:
        cursor.close()
        db.close()
        return "STOCK_INSUFICIENTE", False

    total = med["preco"] * quantidade
    
    cursor.execute(
        "INSERT INTO vendas (id_medicamento, id_cliente, id_farmaceutico, quantidade, total, metodo_pagamento) VALUES (%s, %s, %s, %s, %s, %s)",
        (id_med, id_cliente, id_farmaceutico, quantidade, total, metodo)
    )
    
    novo_stock = med["stock"] - quantidade
    cursor.execute("UPDATE medicamentos SET stock = %s WHERE id = %s", (novo_stock, id_med))
    
    db.commit()
    
    stock_baixo = novo_stock <= med["stock_minimo"]
    
    cursor.close()
    db.close()
    return "COMPRA_CONFIRMADA", stock_baixo