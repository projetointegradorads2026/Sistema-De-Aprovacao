CREATE DATABASE sistema_aprovacao
  DEFAULT CHARACTER SET utf8mb4
  DEFAULT COLLATE utf8mb4_unicode_ci;

USE sistema_aprovacao;

-- 2. Tabela: departamento
CREATE TABLE departamento (
    id INT AUTO_INCREMENT PRIMARY KEY,
    descricao VARCHAR(120) NOT NULL
);

-- 3. Tabela: usuario
CREATE TABLE usuario (
    id INT AUTO_INCREMENT PRIMARY KEY,
    departamento_id INT NOT NULL,
    nome VARCHAR(120) NOT NULL,
    email VARCHAR(150) NOT NULL UNIQUE,
    senha VARCHAR(255) NOT NULL,
    perfil VARCHAR(50) NOT NULL,
    cargo VARCHAR(80) NOT NULL,
    ativo BOOLEAN NOT NULL DEFAULT TRUE,
    criado_em DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_usuario_departamento FOREIGN KEY (departamento_id) REFERENCES departamento(id) ON UPDATE CASCADE ON DELETE RESTRICT
);

-- 4. Tabela: tipo_requisicao
CREATE TABLE tipo_requisicao (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(100) NOT NULL UNIQUE,
    descricao VARCHAR(255) NULL,
    ativo BOOLEAN NOT NULL DEFAULT TRUE
);

-- 5. Tabela: requisicao
CREATE TABLE requisicao (
    id INT AUTO_INCREMENT PRIMARY KEY,
    tipo_requisicao_id INT NOT NULL,
    solicitante_id INT NOT NULL,
    departamento_id INT NOT NULL,
    cargo_solicitado VARCHAR(80) NOT NULL,
    quantidade INT NOT NULL DEFAULT 1,
    descricao TEXT NOT NULL,
    justificativa TEXT NOT NULL,
    status_aprovacao VARCHAR(30) NOT NULL DEFAULT 'EM ANDAMENTO',
    criada_em DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    atualizada_em DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT fk_requisicao_tipo FOREIGN KEY (tipo_requisicao_id) REFERENCES tipo_requisicao(id) ON UPDATE CASCADE ON DELETE RESTRICT,
    CONSTRAINT fk_requisicao_solicitante FOREIGN KEY (solicitante_id) REFERENCES usuario(id) ON UPDATE CASCADE ON DELETE RESTRICT, 
    CONSTRAINT fk_requisicao_departamento FOREIGN KEY (departamento_id) REFERENCES departamento(id) ON UPDATE CASCADE ON DELETE RESTRICT
);


-- Inserir departamentos
INSERT INTO departamento (descricao) VALUES 
('Tecnologia da Informação'),
('Recursos Humanos'),
('Financeiro');

-- Inserir usuários
INSERT INTO usuario (departamento_id, nome, email, senha, perfil, cargo, ativo) VALUES 
(1, 'Carlos Silva', 'carlos@empresa.com', '123456', 'SOLICITANTE', 'Analista de Sistemas', TRUE),
(1, 'Mariana Souza', 'mariana@empresa.com', '123456', 'APROVADOR', 'Gerente de TI', TRUE);

-- Inserir tipos de requisição
INSERT INTO tipo_requisicao (nome, descricao, ativo) VALUES 
('Aumento de Quadro', 'Contratação para expansão da equipe', TRUE),
('Substituição', 'Substituição de funcionário desligado', TRUE);
