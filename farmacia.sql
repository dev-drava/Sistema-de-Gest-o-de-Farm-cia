CREATE TABLE utilizador (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(100) NOT NULL,
    palavra_passe_hash VARCHAR(255) NOT NULL,
    tipo ENUM('admin', 'farmaceutico', 'cliente') NOT NULL
);

CREATE TABLE medicamentos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(100) NOT NULL,
    categoria VARCHAR(50),
    preco DECIMAL(10,2) NOT NULL,
    stock INT NOT NULL DEFAULT 0,
    stock_minimo INT NOT NULL DEFAULT 5,
    validade DATE
);

CREATE TABLE vendas (
    id INT AUTO_INCREMENT PRIMARY KEY,
    id_medicamento INT NOT NULL,
    id_cliente INT NOT NULL,
    id_farmaceutico INT NULL,
    quantidade INT NOT NULL,
    total DECIMAL(10,2) NOT NULL,
    metodo_pagamento ENUM('dinheiro', 'cartao', 'outro') DEFAULT 'dinheiro',
    data_venda DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (id_medicamento) REFERENCES medicamentos(id),
    FOREIGN KEY (id_cliente) REFERENCES utilizador(id),
    FOREIGN KEY (id_farmaceutico) REFERENCES utilizador(id)
);