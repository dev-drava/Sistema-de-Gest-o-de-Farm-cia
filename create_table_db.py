from connect_db import start_connection

mydb = start_connection()
mycursor = mydb.cursor()

mycursor.execute("""
    CREATE TABLE IF NOT EXISTS utilizador (
        id INT AUTO_INCREMENT PRIMARY KEY,
        nome VARCHAR(255) NOT NULL UNIQUE,
        palavra_passe_hash VARCHAR(255) NOT NULL,
        tipo VARCHAR(50) NOT NULL
    )
""")

mycursor.execute("""
    CREATE TABLE IF NOT EXISTS medicamentos (
        id INT AUTO_INCREMENT PRIMARY KEY,
        nome VARCHAR(255) NOT NULL,
        categoria VARCHAR(255),
        preco DECIMAL(10,2) NOT NULL,
        stock INT NOT NULL,
        stock_minimo INT DEFAULT 5,
        validade DATE,
        ativo TINYINT DEFAULT 1
    )
""")

mycursor.execute("""
    CREATE TABLE IF NOT EXISTS vendas (
        id INT AUTO_INCREMENT PRIMARY KEY,
        id_medicamento INT,
        id_cliente INT,
        id_farmaceutico INT,
        quantidade INT NOT NULL,
        total DECIMAL(10,2) NOT NULL,
        metodo_pagamento VARCHAR(50),
        data_venda TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (id_medicamento) REFERENCES medicamentos(id),
        FOREIGN KEY (id_cliente) REFERENCES utilizador(id),
        FOREIGN KEY (id_farmaceutico) REFERENCES utilizador(id)
    )
""")

print("Tabelas da farmácia criadas com sucesso!")