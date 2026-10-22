# Sistema de Aprovação de Requisição de Pessoal — API REST (MySQL)

API REST desenvolvida em **Python** e **Flask** com banco de dados **MySQL** estruturada com separação entre entidades e endpoints.

---

## 📁 Estrutura de Arquivos

```text
API - Sistema Aprovacao/
├── models.py            # Contém a instância db e as 4 entidades (Departamento, Usuario, TipoRequisicao, Requisicao)
├── main.py              # Contém a instância do Flask, configuração do MySQL e todos os endpoints (rotas)
├── app.py               # Ponto de entrada alternativo para iniciar a aplicação
├── test_api.py          # Testes automatizados validando endpoints e regras
├── requirements.txt     # Dependências do projeto
├── README.md            # Documentação e instruções de uso
└── database/
    └── schema.sql       # Script SQL para criação das tabelas no MySQL
```

---

## 🔧 Separação das Instâncias

- **[models.py](file:///c:/API%20-%20Sistema%20Aprovacao/models.py)**: Define a instância `db = SQLAlchemy()` desvinculada e declara as classes de entidades.
- **[main.py](file:///c:/API%20-%20Sistema%20Aprovacao/main.py)**: Cria a aplicação Flask `app = Flask(__name__)`, configura as credenciais do banco e executa `db.init_app(app)` para vincular a instância do banco à aplicação. Também implementa todos os endpoints da API.

---

## 📌 Principais Endpoints

### Departamentos
- `GET /departamentos`
- `GET /departamentos/<id>`
- `POST /departamentos`
- `PUT /departamentos/<id>`
- `DELETE /departamentos/<id>`

### Usuários
- `GET /usuarios`
- `GET /usuarios/<id>`
- `POST /usuarios`
- `PUT /usuarios/<id>`
- `DELETE /usuarios/<id>`

### Tipos de Requisição
- `GET /tipos-requisicao`
- `GET /tipos-requisicao/<id>`
- `POST /tipos-requisicao`
- `PUT /tipos-requisicao/<id>`
- `DELETE /tipos-requisicao/<id>`

### Requisições
- `GET /requisicoes`
- `GET /requisicoes/<id>`
- `POST /requisicoes` *(inicia com `status_aprovacao = "EM ANDAMENTO"`)*
- `PUT /requisicoes/<id>`
- `PUT /requisicoes/<id>/status` *(aprova ou reprova: `{"status_aprovacao": "APROVADO"}` ou `"REPROVADO"`)*
- `DELETE /requisicoes/<id>`

---

## 🚀 Como Executar

1. Crie o banco no MySQL executando o script `database/schema.sql`.
2. Inicie o servidor:
   ```powershell
   python main.py
   ```
   *(ou `python app.py`)*
