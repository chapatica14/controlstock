-- ============================================================
--  ControloStock · Base de Dados
--  Autor : Gonçalo Chapatica
--  Curso : Licenciatura em Informática · 3.º Ano
-- ============================================================

CREATE DATABASE IF NOT EXISTS controlstock;
USE controlstock;

-- Tabela de utilizadores
CREATE TABLE IF NOT EXISTS utilizadores (
    id           INT           AUTO_INCREMENT PRIMARY KEY,
    nome         VARCHAR(100)  NOT NULL,
    username     VARCHAR(50)   NOT NULL UNIQUE,
    email        VARCHAR(100)  NOT NULL UNIQUE,
    senha        VARCHAR(64)   NOT NULL,
    data_registo TIMESTAMP     DEFAULT CURRENT_TIMESTAMP
);

-- Tabela de produtos
CREATE TABLE IF NOT EXISTS produtos (
    id           INT            AUTO_INCREMENT PRIMARY KEY,
    nome         VARCHAR(100)   NOT NULL,
    categoria    VARCHAR(100)   NOT NULL,
    quantidade   INT            NOT NULL DEFAULT 0,
    preco        DECIMAL(10,2)  NOT NULL,
    data_registo TIMESTAMP      DEFAULT CURRENT_TIMESTAMP
);

-- Conta de administrador padrão
-- username: admin | senha: admin123
INSERT IGNORE INTO utilizadores (nome, username, email, senha) VALUES (
    'Administrador',
    'admin',
    'admin@controlstock.mz',
    '240be518fabd2724ddb6f04eeb1da5967448d7e831c08c8fa822809f74c720a9'
);

-- Dados de exemplo
INSERT INTO produtos (nome, categoria, quantidade, preco) VALUES
    ('Arroz (5kg)',              'Alimentação',  120,  350.00),
    ('Óleo de Soja (1L)',        'Alimentação',   85,  120.00),
    ('Caderno A4 (100 folhas)',  'Papelaria',    200,   45.00),
    ('Caneta Bic Azul',         'Papelaria',    500,    5.00),
    ('Sabão em Pó (1kg)',        'Limpeza',       60,   80.00),
    ('Detergente Líquido',       'Limpeza',        7,   55.00);
