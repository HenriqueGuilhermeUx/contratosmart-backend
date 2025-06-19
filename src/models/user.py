from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import json

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    nome_completo = db.Column(db.String(255), nullable=False)
    cpf = db.Column(db.String(14), unique=True)
    telefone = db.Column(db.String(20))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)

    # Relacionamentos
    contracts = db.relationship('Contract', backref='user', lazy=True)
    signatures = db.relationship('DigitalSignature', backref='user', lazy=True)
    activity_logs = db.relationship('ActivityLog', backref='user', lazy=True)

    def __repr__(self):
        return f'<User {self.email}>'

    def to_dict(self):
        return {
            'id': self.id,
            'email': self.email,
            'nome_completo': self.nome_completo,
            'cpf': self.cpf,
            'telefone': self.telefone,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'is_active': self.is_active
        }

class ContractType(db.Model):
    __tablename__ = 'contract_types'
    
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    descricao = db.Column(db.Text)
    categoria = db.Column(db.Enum('servico', 'namoro', 'pets', 'aluguel', 'outros', name='categoria_enum'), nullable=False)
    template_path = db.Column(db.String(255))
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relacionamentos
    templates = db.relationship('ContractTemplate', backref='contract_type', lazy=True)
    contracts = db.relationship('Contract', backref='contract_type', lazy=True)

    def to_dict(self):
        return {
            'id': self.id,
            'nome': self.nome,
            'descricao': self.descricao,
            'categoria': self.categoria,
            'template_path': self.template_path,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class ContractTemplate(db.Model):
    __tablename__ = 'contract_templates'
    
    id = db.Column(db.Integer, primary_key=True)
    contract_type_id = db.Column(db.Integer, db.ForeignKey('contract_types.id'), nullable=False)
    nome = db.Column(db.String(255), nullable=False)
    conteudo_template = db.Column(db.Text, nullable=False)
    campos_obrigatorios = db.Column(db.Text)  # JSON string
    campos_opcionais = db.Column(db.Text)     # JSON string
    versao = db.Column(db.String(10), default='1.0')
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relacionamentos
    contracts = db.relationship('Contract', backref='template', lazy=True)

    def get_campos_obrigatorios(self):
        if self.campos_obrigatorios:
            return json.loads(self.campos_obrigatorios)
        return {}

    def set_campos_obrigatorios(self, campos):
        self.campos_obrigatorios = json.dumps(campos)

    def get_campos_opcionais(self):
        if self.campos_opcionais:
            return json.loads(self.campos_opcionais)
        return {}

    def set_campos_opcionais(self, campos):
        self.campos_opcionais = json.dumps(campos)

    def to_dict(self):
        return {
            'id': self.id,
            'contract_type_id': self.contract_type_id,
            'nome': self.nome,
            'conteudo_template': self.conteudo_template,
            'campos_obrigatorios': self.get_campos_obrigatorios(),
            'campos_opcionais': self.get_campos_opcionais(),
            'versao': self.versao,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class Contract(db.Model):
    __tablename__ = 'contracts'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    contract_type_id = db.Column(db.Integer, db.ForeignKey('contract_types.id'), nullable=False)
    template_id = db.Column(db.Integer, db.ForeignKey('contract_templates.id'), nullable=False)
    titulo = db.Column(db.String(255), nullable=False)
    dados_contrato = db.Column(db.Text, nullable=False)  # JSON string
    conteudo_final = db.Column(db.Text)
    status = db.Column(db.Enum('rascunho', 'gerado', 'assinado', 'cancelado', name='status_enum'), default='rascunho')
    hash_documento = db.Column(db.String(64))
    url_documento = db.Column(db.String(500))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relacionamentos
    parties = db.relationship('ContractParty', backref='contract', lazy=True, cascade='all, delete-orphan')
    signatures = db.relationship('DigitalSignature', backref='contract', lazy=True, cascade='all, delete-orphan')
    activity_logs = db.relationship('ActivityLog', backref='contract', lazy=True)

    def get_dados_contrato(self):
        if self.dados_contrato:
            return json.loads(self.dados_contrato)
        return {}

    def set_dados_contrato(self, dados):
        self.dados_contrato = json.dumps(dados)

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'contract_type_id': self.contract_type_id,
            'template_id': self.template_id,
            'titulo': self.titulo,
            'dados_contrato': self.get_dados_contrato(),
            'conteudo_final': self.conteudo_final,
            'status': self.status,
            'hash_documento': self.hash_documento,
            'url_documento': self.url_documento,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class ContractParty(db.Model):
    __tablename__ = 'contract_parties'
    
    id = db.Column(db.Integer, primary_key=True)
    contract_id = db.Column(db.Integer, db.ForeignKey('contracts.id'), nullable=False)
    tipo_parte = db.Column(db.Enum('contratante', 'contratado', 'testemunha', name='tipo_parte_enum'), nullable=False)
    nome_completo = db.Column(db.String(255), nullable=False)
    cpf = db.Column(db.String(14))
    rg = db.Column(db.String(20))
    endereco = db.Column(db.Text)
    telefone = db.Column(db.String(20))
    email = db.Column(db.String(255))
    profissao = db.Column(db.String(100))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'contract_id': self.contract_id,
            'tipo_parte': self.tipo_parte,
            'nome_completo': self.nome_completo,
            'cpf': self.cpf,
            'rg': self.rg,
            'endereco': self.endereco,
            'telefone': self.telefone,
            'email': self.email,
            'profissao': self.profissao,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class DigitalSignature(db.Model):
    __tablename__ = 'digital_signatures'
    
    id = db.Column(db.Integer, primary_key=True)
    contract_id = db.Column(db.Integer, db.ForeignKey('contracts.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    tipo_assinatura = db.Column(db.Enum('govbr', 'certificado_digital', 'simples', name='tipo_assinatura_enum'), nullable=False)
    hash_assinatura = db.Column(db.String(255))
    certificado_info = db.Column(db.Text)  # JSON string
    timestamp_assinatura = db.Column(db.DateTime)
    ip_address = db.Column(db.String(45))
    user_agent = db.Column(db.Text)
    status = db.Column(db.Enum('pendente', 'assinado', 'rejeitado', 'expirado', name='status_assinatura_enum'), default='pendente')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def get_certificado_info(self):
        if self.certificado_info:
            return json.loads(self.certificado_info)
        return {}

    def set_certificado_info(self, info):
        self.certificado_info = json.dumps(info)

    def to_dict(self):
        return {
            'id': self.id,
            'contract_id': self.contract_id,
            'user_id': self.user_id,
            'tipo_assinatura': self.tipo_assinatura,
            'hash_assinatura': self.hash_assinatura,
            'certificado_info': self.get_certificado_info(),
            'timestamp_assinatura': self.timestamp_assinatura.isoformat() if self.timestamp_assinatura else None,
            'ip_address': self.ip_address,
            'user_agent': self.user_agent,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class SystemSetting(db.Model):
    __tablename__ = 'system_settings'
    
    id = db.Column(db.Integer, primary_key=True)
    chave = db.Column(db.String(100), unique=True, nullable=False)
    valor = db.Column(db.Text)
    descricao = db.Column(db.Text)
    tipo = db.Column(db.Enum('string', 'number', 'boolean', 'json', name='tipo_setting_enum'), default='string')
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def get_valor(self):
        if self.tipo == 'json' and self.valor:
            return json.loads(self.valor)
        elif self.tipo == 'boolean':
            return self.valor.lower() == 'true' if self.valor else False
        elif self.tipo == 'number':
            return float(self.valor) if self.valor else 0
        return self.valor

    def set_valor(self, valor):
        if self.tipo == 'json':
            self.valor = json.dumps(valor)
        elif self.tipo == 'boolean':
            self.valor = str(valor).lower()
        else:
            self.valor = str(valor)

    def to_dict(self):
        return {
            'id': self.id,
            'chave': self.chave,
            'valor': self.get_valor(),
            'descricao': self.descricao,
            'tipo': self.tipo,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class ActivityLog(db.Model):
    __tablename__ = 'activity_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    contract_id = db.Column(db.Integer, db.ForeignKey('contracts.id'))
    acao = db.Column(db.String(100), nullable=False)
    detalhes = db.Column(db.Text)  # JSON string
    ip_address = db.Column(db.String(45))
    user_agent = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def get_detalhes(self):
        if self.detalhes:
            return json.loads(self.detalhes)
        return {}

    def set_detalhes(self, detalhes):
        self.detalhes = json.dumps(detalhes)

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'contract_id': self.contract_id,
            'acao': self.acao,
            'detalhes': self.get_detalhes(),
            'ip_address': self.ip_address,
            'user_agent': self.user_agent,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

