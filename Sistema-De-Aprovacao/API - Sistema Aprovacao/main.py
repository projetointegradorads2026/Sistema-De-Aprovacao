import os
from flask import Flask, jsonify, request
from models import (
    db,
    Departamento,
    Usuario,
    TipoRequisicao,
    Requisicao,
    STATUS_APROVACAO_PERMITIDOS,
    PERFIS_USUARIO,
    agora_utc
)

app = Flask(__name__)

# Configurações do MySQL
DB_USER = os.getenv('DB_USER', 'root')
DB_PASSWORD = os.getenv('DB_PASSWORD', '')
DB_HOST = os.getenv('DB_HOST', 'localhost')
DB_PORT = os.getenv('DB_PORT', '3306')
DB_NAME = os.getenv('DB_NAME', 'sistema_aprovacao')

DEFAULT_MYSQL_URI = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}?charset=utf8mb4"

app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', DEFAULT_MYSQL_URI)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JSON_SORT_KEYS'] = False


db.init_app(app)

@app.route('/', methods=['GET'])
def index():
    return jsonify({
        'mensagem': 'API REST — Sistema de Aprovação de Requisição de Pessoal',
        'status': 'Ativa',
        'endpoints': {
            'departamentos': '/departamentos',
            'usuarios': '/usuarios',
            'tipos_requisicao': '/tipos-requisicao',
            'requisicoes': '/requisicoes',
            'alterar_status_aprovacao': '/requisicoes/<id>/status'
        }
    }), 200


# ENDPOINTS: DEPARTAMENTOS

@app.route('/departamentos', methods=['GET'])
def listar_departamentos():
    departamentos = Departamento.query.all()
    return jsonify([d.to_dict() for d in departamentos]), 200


@app.route('/departamentos/<int:id>', methods=['GET'])
def obter_departamento(id):
    d = db.session.get(Departamento, id)
    if not d:
        return jsonify({'erro': f'Departamento ID {id} não encontrado.'}), 404
    return jsonify(d.to_dict()), 200


@app.route('/departamentos', methods=['POST'])
def criar_departamento():
    dados = request.get_json()
    if not dados or not dados.get('descricao') or not str(dados.get('descricao')).strip():
        return jsonify({'erro': 'O campo "descricao" é obrigatório.'}), 400

    novo_dep = Departamento(descricao=str(dados['descricao']).strip())
    db.session.add(novo_dep)
    db.session.commit()
    return jsonify(novo_dep.to_dict()), 201


@app.route('/departamentos/<int:id>', methods=['PUT'])
def atualizar_departamento(id):
    d = db.session.get(Departamento, id)
    if not d:
        return jsonify({'erro': f'Departamento ID {id} não encontrado.'}), 404

    dados = request.get_json()
    if not dados or not dados.get('descricao') or not str(dados.get('descricao')).strip():
        return jsonify({'erro': 'O campo "descricao" é obrigatório.'}), 400

    d.descricao = str(dados['descricao']).strip()
    db.session.commit()
    return jsonify(d.to_dict()), 200


@app.route('/departamentos/<int:id>', methods=['DELETE'])
def excluir_departamento(id):
    d = db.session.get(Departamento, id)
    if not d:
        return jsonify({'erro': f'Departamento ID {id} não encontrado.'}), 404

    if d.usuarios:
        return jsonify({'erro': 'Não é possível excluir: existem usuários vinculados a este departamento.'}), 400

    if d.requisicoes:
        return jsonify({'erro': 'Não é possível excluir: existem requisições vinculadas a este departamento.'}), 400

    db.session.delete(d)
    db.session.commit()
    return jsonify({'mensagem': f'Departamento ID {id} excluído com sucesso.'}), 200


# ENDPOINTS: USUÁRIOS

@app.route('/usuarios', methods=['GET'])
def listar_usuarios():
    usuarios = Usuario.query.all()
    return jsonify([u.to_dict() for u in usuarios]), 200


@app.route('/usuarios/<int:id>', methods=['GET'])
def obter_usuario(id):
    u = db.session.get(Usuario, id)
    if not u:
        return jsonify({'erro': f'Usuário ID {id} não encontrado.'}), 404
    return jsonify(u.to_dict()), 200


@app.route('/usuarios', methods=['POST'])
def criar_usuario():
    dados = request.get_json()
    if not dados:
        return jsonify({'erro': 'Corpo da requisição JSON não fornecido.'}), 400

    campos = ['nome', 'email', 'senha', 'perfil', 'cargo', 'departamento_id']
    for c in campos:
        if c not in dados or dados[c] is None or str(dados[c]).strip() == '':
            return jsonify({'erro': f'O campo "{c}" é obrigatório.'}), 400

    departamento_id = dados['departamento_id']
    if not db.session.get(Departamento, departamento_id):
        return jsonify({'erro': f'Departamento ID {departamento_id} não existe.'}), 404

    email = str(dados['email']).strip().lower()
    if Usuario.query.filter_by(email=email).first():
        return jsonify({'erro': f'O e-mail "{email}" já está cadastrado.'}), 400

    perfil = str(dados['perfil']).strip().upper()
    if perfil not in PERFIS_USUARIO:
        return jsonify({'erro': f'Perfil inválido. Permitidos: {PERFIS_USUARIO}'}), 400

    novo_usuario = Usuario(
        departamento_id=departamento_id,
        nome=str(dados['nome']).strip(),
        email=email,
        senha=str(dados['senha']).strip(),
        perfil=perfil,
        cargo=str(dados['cargo']).strip(),
        ativo=bool(dados.get('ativo', True))
    )
    db.session.add(novo_usuario)
    db.session.commit()
    return jsonify(novo_usuario.to_dict()), 201


@app.route('/usuarios/<int:id>', methods=['PUT'])
def atualizar_usuario(id):
    u = db.session.get(Usuario, id)
    if not u:
        return jsonify({'erro': f'Usuário ID {id} não encontrado.'}), 404

    dados = request.get_json()
    if not dados:
        return jsonify({'erro': 'Corpo da requisição JSON não fornecido.'}), 400

    if 'departamento_id' in dados:
        if not db.session.get(Departamento, dados['departamento_id']):
            return jsonify({'erro': f'Departamento ID {dados["departamento_id"]} não existe.'}), 404
        u.departamento_id = dados['departamento_id']

    if 'email' in dados:
        email = str(dados['email']).strip().lower()
        existente = Usuario.query.filter_by(email=email).first()
        if existente and existente.id != id:
            return jsonify({'erro': f'O e-mail "{email}" já pertence a outro usuário.'}), 400
        u.email = email

    if 'perfil' in dados:
        perfil = str(dados['perfil']).strip().upper()
        if perfil not in PERFIS_USUARIO:
            return jsonify({'erro': f'Perfil inválido. Permitidos: {PERFIS_USUARIO}'}), 400
        u.perfil = perfil

    if 'nome' in dados and str(dados['nome']).strip():
        u.nome = str(dados['nome']).strip()

    if 'cargo' in dados and str(dados['cargo']).strip():
        u.cargo = str(dados['cargo']).strip()

    if 'senha' in dados and str(dados['senha']).strip():
        u.senha = str(dados['senha']).strip()

    if 'ativo' in dados:
        u.ativo = bool(dados['ativo'])

    db.session.commit()
    return jsonify(u.to_dict()), 200


@app.route('/usuarios/<int:id>', methods=['DELETE'])
def excluir_usuario(id):
    u = db.session.get(Usuario, id)
    if not u:
        return jsonify({'erro': f'Usuário ID {id} não encontrado.'}), 404

    if u.requisicoes:
        return jsonify({'erro': 'Não é possível excluir: o usuário possui requisições vinculadas.'}), 400

    db.session.delete(u)
    db.session.commit()
    return jsonify({'mensagem': f'Usuário ID {id} excluído com sucesso.'}), 200


# ENDPOINTS: TIPOS DE REQUISIÇÃO

@app.route('/tipos-requisicao', methods=['GET'])
def listar_tipos_requisicao():
    tipos = TipoRequisicao.query.all()
    return jsonify([t.to_dict() for t in tipos]), 200


@app.route('/tipos-requisicao/<int:id>', methods=['GET'])
def obter_tipo_requisicao(id):
    t = db.session.get(TipoRequisicao, id)
    if not t:
        return jsonify({'erro': f'Tipo de requisição ID {id} não encontrado.'}), 404
    return jsonify(t.to_dict()), 200


@app.route('/tipos-requisicao', methods=['POST'])
def criar_tipo_requisicao():
    dados = request.get_json()
    if not dados or not dados.get('nome') or not str(dados.get('nome')).strip():
        return jsonify({'erro': 'O campo "nome" é obrigatório.'}), 400

    nome = str(dados['nome']).strip()
    if TipoRequisicao.query.filter_by(nome=nome).first():
        return jsonify({'erro': f'Tipo de requisição "{nome}" já existe.'}), 400

    novo_tipo = TipoRequisicao(
        nome=nome,
        descricao=dados.get('descricao'),
        ativo=bool(dados.get('ativo', True))
    )
    db.session.add(novo_tipo)
    db.session.commit()
    return jsonify(novo_tipo.to_dict()), 201


@app.route('/tipos-requisicao/<int:id>', methods=['PUT'])
def atualizar_tipo_requisicao(id):
    t = db.session.get(TipoRequisicao, id)
    if not t:
        return jsonify({'erro': f'Tipo de requisição ID {id} não encontrado.'}), 404

    dados = request.get_json()
    if not dados:
        return jsonify({'erro': 'Corpo da requisição JSON não fornecido.'}), 400

    if 'nome' in dados and str(dados['nome']).strip():
        nome = str(dados['nome']).strip()
        existente = TipoRequisicao.query.filter_by(nome=nome).first()
        if existente and existente.id != id:
            return jsonify({'erro': f'Tipo de requisição "{nome}" já cadastrado.'}), 400
        t.nome = nome

    if 'descricao' in dados:
        t.descricao = dados['descricao']

    if 'ativo' in dados:
        t.ativo = bool(dados['ativo'])

    db.session.commit()
    return jsonify(t.to_dict()), 200


@app.route('/tipos-requisicao/<int:id>', methods=['DELETE'])
def excluir_tipo_requisicao(id):
    t = db.session.get(TipoRequisicao, id)
    if not t:
        return jsonify({'erro': f'Tipo de requisição ID {id} não encontrado.'}), 404

    if t.requisicoes:
        return jsonify({'erro': 'Não é possível excluir: existem requisições vinculadas a este tipo.'}), 400

    db.session.delete(t)
    db.session.commit()
    return jsonify({'mensagem': f'Tipo de requisição ID {id} excluído com sucesso.'}), 200

# ENDPOINTS: REQUISIÇÕES (COM STATUS DE APROVAÇÃO)

@app.route('/requisicoes', methods=['GET'])
def listar_requisicoes():
    requisicoes = Requisicao.query.all()
    return jsonify([r.to_dict() for r in requisicoes]), 200


@app.route('/requisicoes/<int:id>', methods=['GET'])
def obter_requisicao(id):
    r = db.session.get(Requisicao, id)
    if not r:
        return jsonify({'erro': f'Requisição ID {id} não encontrada.'}), 404
    return jsonify(r.to_dict()), 200


@app.route('/requisicoes', methods=['POST'])
def criar_requisicao():
    """
    Cria uma nova requisição.
    Regra: O campo status_aprovacao inicia automaticamente como 'EM ANDAMENTO'.
    """
    dados = request.get_json()
    if not dados:
        return jsonify({'erro': 'Corpo da requisição JSON não fornecido.'}), 400

    campos = [
        'tipo_requisicao_id',
        'solicitante_id',
        'departamento_id',
        'cargo_solicitado',
        'descricao',
        'justificativa'
    ]
    for c in campos:
        if c not in dados or dados[c] is None or str(dados[c]).strip() == '':
            return jsonify({'erro': f'O campo "{c}" é obrigatório.'}), 400

    # Validação de chaves estrangeiras
    if not db.session.get(TipoRequisicao, dados['tipo_requisicao_id']):
        return jsonify({'erro': f'Tipo de requisição ID {dados["tipo_requisicao_id"]} não existe.'}), 404

    if not db.session.get(Usuario, dados['solicitante_id']):
        return jsonify({'erro': f'Usuário solicitante ID {dados["solicitante_id"]} não existe.'}), 404

    if not db.session.get(Departamento, dados['departamento_id']):
        return jsonify({'erro': f'Departamento ID {dados["departamento_id"]} não existe.'}), 404

    quantidade = int(dados.get('quantidade', 1))
    if quantidade < 1:
        return jsonify({'erro': 'A quantidade de vagas deve ser de no mínimo 1.'}), 400

    nova_requisicao = Requisicao(
        tipo_requisicao_id=dados['tipo_requisicao_id'],
        solicitante_id=dados['solicitante_id'],
        departamento_id=dados['departamento_id'],
        cargo_solicitado=str(dados['cargo_solicitado']).strip(),
        quantidade=quantidade,
        descricao=str(dados['descricao']).strip(),
        justificativa=str(dados['justificativa']).strip(),
        status_aprovacao='EM ANDAMENTO'
    )

    db.session.add(nova_requisicao)
    db.session.commit()
    return jsonify(nova_requisicao.to_dict()), 201


@app.route('/requisicoes/<int:id>', methods=['PUT'])
def atualizar_requisicao(id):
    r = db.session.get(Requisicao, id)
    if not r:
        return jsonify({'erro': f'Requisição ID {id} não encontrada.'}), 404

    dados = request.get_json()
    if not dados:
        return jsonify({'erro': 'Corpo da requisição JSON não fornecido.'}), 400

    if 'tipo_requisicao_id' in dados:
        if not db.session.get(TipoRequisicao, dados['tipo_requisicao_id']):
            return jsonify({'erro': f'Tipo de requisição ID {dados["tipo_requisicao_id"]} não existe.'}), 404
        r.tipo_requisicao_id = dados['tipo_requisicao_id']

    if 'solicitante_id' in dados:
        if not db.session.get(Usuario, dados['solicitante_id']):
            return jsonify({'erro': f'Usuário solicitante ID {dados["solicitante_id"]} não existe.'}), 404
        r.solicitante_id = dados['solicitante_id']

    if 'departamento_id' in dados:
        if not db.session.get(Departamento, dados['departamento_id']):
            return jsonify({'erro': f'Departamento ID {dados["departamento_id"]} não existe.'}), 404
        r.departamento_id = dados['departamento_id']

    if 'cargo_solicitado' in dados and str(dados['cargo_solicitado']).strip():
        r.cargo_solicitado = str(dados['cargo_solicitado']).strip()

    if 'quantidade' in dados:
        qtd = int(dados['quantidade'])
        if qtd < 1:
            return jsonify({'erro': 'Quantidade deve ser no mínimo 1.'}), 400
        r.quantidade = qtd

    if 'descricao' in dados and str(dados['descricao']).strip():
        r.descricao = str(dados['descricao']).strip()

    if 'justificativa' in dados and str(dados['justificativa']).strip():
        r.justificativa = str(dados['justificativa']).strip()

    if 'status_aprovacao' in dados:
        st = str(dados['status_aprovacao']).strip().upper()
        if st not in STATUS_APROVACAO_PERMITIDOS:
            return jsonify({'erro': f'status_aprovacao inválido. Permitidos: {STATUS_APROVACAO_PERMITIDOS}'}), 400
        r.status_aprovacao = st

    r.atualizada_em = agora_utc()
    db.session.commit()
    return jsonify(r.to_dict()), 200


@app.route('/requisicoes/<int:id>/status', methods=['PUT', 'PATCH'])
def alterar_status_aprovacao(id):
    """
    Endpoint para APROVAR ou REPROVAR a requisição.
    Recebe no corpo JSON: {"status_aprovacao": "APROVADO"} ou {"status_aprovacao": "REPROVADO"}.
    """
    r = db.session.get(Requisicao, id)
    if not r:
        return jsonify({'erro': f'Requisição ID {id} não encontrada.'}), 404

    dados = request.get_json()
    if not dados or not dados.get('status_aprovacao'):
        return jsonify({
            'erro': f'O campo "status_aprovacao" é obrigatório. Permitidos: {STATUS_APROVACAO_PERMITIDOS}'
        }), 400

    novo_status = str(dados['status_aprovacao']).strip().upper()
    if novo_status not in STATUS_APROVACAO_PERMITIDOS:
        return jsonify({
            'erro': f'Valor inválido para status_aprovacao. Permitidos: {STATUS_APROVACAO_PERMITIDOS}'
        }), 400

    r.status_aprovacao = novo_status
    r.atualizada_em = agora_utc()
    db.session.commit()

    return jsonify({
        'mensagem': f'Status da requisição ID {id} atualizado com sucesso para "{novo_status}".',
        'requisicao': r.to_dict()
    }), 200


@app.route('/requisicoes/<int:id>', methods=['DELETE'])
def excluir_requisicao(id):
    r = db.session.get(Requisicao, id)
    if not r:
        return jsonify({'erro': f'Requisição ID {id} não encontrada.'}), 404

    db.session.delete(r)
    db.session.commit()
    return jsonify({'mensagem': f'Requisição ID {id} excluída com sucesso.'}), 200

@app.errorhandler(404)
def nao_encontrado(erro):
    return jsonify({'erro': 'Recurso ou rota não encontrada.'}), 404


@app.errorhandler(400)
def requisicao_invalida(erro):
    return jsonify({'erro': 'Requisição inválida.'}), 400


@app.errorhandler(500)
def erro_interno(erro):
    return jsonify({'erro': 'Erro interno do servidor.'}), 500

if __name__ == '__main__':
    print("Iniciando a API de Aprovação de Requisições...")
    print("Acesse http://127.0.0.1:5000/ no seu navegador ou Postman.")
    app.run(debug=True, host='0.0.0.0', port=5000)
