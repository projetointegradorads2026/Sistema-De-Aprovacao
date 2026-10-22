from datetime import datetime, timezone
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

def agora_utc():
    """Retorna data e hora atual em formato UTC sem fuso para persistência."""
    return datetime.now(timezone.utc).replace(tzinfo=None)

# Constantes e valores permitidos
STATUS_APROVACAO_PERMITIDOS = ['EM ANDAMENTO', 'APROVADO', 'REPROVADO']
PERFIS_USUARIO = ['SOLICITANTE', 'APROVADOR', 'ADMINISTRADOR']


class Departamento(db.Model):
    __tablename__ = 'departamento'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    descricao = db.Column(db.String(120), nullable=False)

    # Relacionamentos
    usuarios = db.relationship('Usuario', backref='departamento', lazy=True)
    requisicoes = db.relationship('Requisicao', backref='departamento', lazy=True)

    def to_dict(self):
        return {
            'id': self.id,
            'descricao': self.descricao
        }


class Usuario(db.Model):
    __tablename__ = 'usuario'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    departamento_id = db.Column(db.Integer, db.ForeignKey('departamento.id'), nullable=False)
    nome = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    senha = db.Column(db.String(255), nullable=False)
    perfil = db.Column(db.String(50), nullable=False, default='SOLICITANTE')
    cargo = db.Column(db.String(80), nullable=False)
    ativo = db.Column(db.Boolean, default=True, nullable=False)
    criado_em = db.Column(db.DateTime, default=agora_utc, nullable=False)

    # Relacionamento com as requisições solicitadas por este usuário
    requisicoes = db.relationship('Requisicao', backref='solicitante', lazy=True)

    def to_dict(self):
        return {
            'id': self.id,
            'departamento_id': self.departamento_id,
            'nome': self.nome,
            'email': self.email,
            'perfil': self.perfil,
            'cargo': self.cargo,
            'ativo': self.ativo,
            'criado_em': self.criado_em.isoformat() if self.criado_em else None
        }


class TipoRequisicao(db.Model):
    __tablename__ = 'tipo_requisicao'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nome = db.Column(db.String(100), unique=True, nullable=False)
    descricao = db.Column(db.String(255), nullable=True)
    ativo = db.Column(db.Boolean, default=True, nullable=False)

    # Relacionamento com as requisições deste tipo
    requisicoes = db.relationship('Requisicao', backref='tipo_requisicao', lazy=True)

    def to_dict(self):
        return {
            'id': self.id,
            'nome': self.nome,
            'descricao': self.descricao,
            'ativo': self.ativo
        }


class Requisicao(db.Model):
    __tablename__ = 'requisicao'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    tipo_requisicao_id = db.Column(db.Integer, db.ForeignKey('tipo_requisicao.id'), nullable=False)
    solicitante_id = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=False)
    departamento_id = db.Column(db.Integer, db.ForeignKey('departamento.id'), nullable=False)

    cargo_solicitado = db.Column(db.String(80), nullable=False)
    quantidade = db.Column(db.Integer, default=1, nullable=False)
    descricao = db.Column(db.Text, nullable=False)
    justificativa = db.Column(db.Text, nullable=False)

    # Status de aprovação: 'EM ANDAMENTO', 'APROVADO' ou 'REPROVADO'
    status_aprovacao = db.Column(db.String(30), default='EM ANDAMENTO', nullable=False)

    criada_em = db.Column(db.DateTime, default=agora_utc, nullable=False)
    atualizada_em = db.Column(db.DateTime, default=agora_utc, onupdate=agora_utc, nullable=False)

    def to_dict(self):
        return {
            'id': self.id,
            'tipo_requisicao_id': self.tipo_requisicao_id,
            'solicitante_id': self.solicitante_id,
            'departamento_id': self.departamento_id,
            'cargo_solicitado': self.cargo_solicitado,
            'quantidade': self.quantidade,
            'descricao': self.descricao,
            'justificativa': self.justificativa,
            'status_aprovacao': self.status_aprovacao,
            'criada_em': self.criada_em.isoformat() if self.criada_em else None,
            'atualizada_em': self.atualizada_em.isoformat() if self.atualizada_em else None
        }
