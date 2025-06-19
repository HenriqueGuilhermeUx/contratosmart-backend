from flask import Blueprint, request, jsonify
from src.models.user import db, ContractType, ContractTemplate, Contract, ContractParty
from datetime import datetime
import hashlib
import re

contracts_bp = Blueprint('contracts', __name__)

@contracts_bp.route('/contract-types', methods=['GET'])
def get_contract_types():
    """Retorna todos os tipos de contratos ativos"""
    try:
        contract_types = ContractType.query.filter_by(is_active=True).all()
        return jsonify({
            'success': True,
            'data': [ct.to_dict() for ct in contract_types]
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@contracts_bp.route('/contract-types/<int:type_id>/templates', methods=['GET'])
def get_templates_by_type(type_id):
    """Retorna todos os templates de um tipo de contrato"""
    try:
        templates = ContractTemplate.query.filter_by(
            contract_type_id=type_id, 
            is_active=True
        ).all()
        return jsonify({
            'success': True,
            'data': [template.to_dict() for template in templates]
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@contracts_bp.route('/templates/<int:template_id>', methods=['GET'])
def get_template(template_id):
    """Retorna um template específico"""
    try:
        template = ContractTemplate.query.get_or_404(template_id)
        return jsonify({
            'success': True,
            'data': template.to_dict()
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@contracts_bp.route('/contracts', methods=['POST'])
def create_contract():
    """Cria um novo contrato"""
    try:
        data = request.get_json()
        
        # Validação básica
        required_fields = ['user_id', 'contract_type_id', 'template_id', 'titulo', 'dados_contrato']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'success': False,
                    'error': f'Campo obrigatório ausente: {field}'
                }), 400

        # Criar o contrato
        contract = Contract(
            user_id=data['user_id'],
            contract_type_id=data['contract_type_id'],
            template_id=data['template_id'],
            titulo=data['titulo']
        )
        contract.set_dados_contrato(data['dados_contrato'])
        
        db.session.add(contract)
        db.session.flush()  # Para obter o ID do contrato

        # Adicionar as partes do contrato
        if 'partes' in data:
            for parte_data in data['partes']:
                parte = ContractParty(
                    contract_id=contract.id,
                    tipo_parte=parte_data['tipo_parte'],
                    nome_completo=parte_data['nome_completo'],
                    cpf=parte_data.get('cpf'),
                    rg=parte_data.get('rg'),
                    endereco=parte_data.get('endereco'),
                    telefone=parte_data.get('telefone'),
                    email=parte_data.get('email'),
                    profissao=parte_data.get('profissao')
                )
                db.session.add(parte)

        db.session.commit()

        return jsonify({
            'success': True,
            'data': contract.to_dict(),
            'message': 'Contrato criado com sucesso'
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@contracts_bp.route('/contracts/<int:contract_id>/generate', methods=['POST'])
def generate_contract(contract_id):
    """Gera o conteúdo final do contrato baseado no template"""
    try:
        contract = Contract.query.get_or_404(contract_id)
        template = ContractTemplate.query.get_or_404(contract.template_id)
        
        # Obter dados do contrato
        dados = contract.get_dados_contrato()
        
        # Gerar conteúdo do contrato
        conteudo_final = generate_contract_content(template.conteudo_template, dados)
        
        # Gerar hash do documento
        hash_documento = hashlib.sha256(conteudo_final.encode('utf-8')).hexdigest()
        
        # Atualizar o contrato
        contract.conteudo_final = conteudo_final
        contract.hash_documento = hash_documento
        contract.status = 'gerado'
        contract.updated_at = datetime.utcnow()
        
        db.session.commit()

        return jsonify({
            'success': True,
            'data': {
                'contract_id': contract.id,
                'conteudo_final': conteudo_final,
                'hash_documento': hash_documento
            },
            'message': 'Contrato gerado com sucesso'
        })

    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@contracts_bp.route('/contracts/<int:contract_id>', methods=['GET'])
def get_contract(contract_id):
    """Retorna um contrato específico"""
    try:
        contract = Contract.query.get_or_404(contract_id)
        
        # Incluir as partes do contrato
        contract_data = contract.to_dict()
        contract_data['partes'] = [parte.to_dict() for parte in contract.parties]
        
        return jsonify({
            'success': True,
            'data': contract_data
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@contracts_bp.route('/contracts', methods=['GET'])
def get_contracts():
    """Retorna contratos do usuário"""
    try:
        user_id = request.args.get('user_id')
        if not user_id:
            return jsonify({
                'success': False,
                'error': 'user_id é obrigatório'
            }), 400

        contracts = Contract.query.filter_by(user_id=user_id).order_by(Contract.created_at.desc()).all()
        
        return jsonify({
            'success': True,
            'data': [contract.to_dict() for contract in contracts]
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

def generate_contract_content(template_content, dados):
    """Gera o conteúdo do contrato substituindo placeholders pelos dados"""
    conteudo = template_content
    
    # Substituir placeholders básicos
    placeholders = {
        '{{CONTRATANTE_NOME}}': dados.get('contratante', {}).get('nome_completo', ''),
        '{{CONTRATANTE_CPF}}': dados.get('contratante', {}).get('cpf', ''),
        '{{CONTRATANTE_RG}}': dados.get('contratante', {}).get('rg', ''),
        '{{CONTRATANTE_ENDERECO}}': dados.get('contratante', {}).get('endereco', ''),
        '{{CONTRATANTE_TELEFONE}}': dados.get('contratante', {}).get('telefone', ''),
        '{{CONTRATANTE_EMAIL}}': dados.get('contratante', {}).get('email', ''),
        
        '{{CONTRATADO_NOME}}': dados.get('contratado', {}).get('nome_completo', ''),
        '{{CONTRATADO_CPF}}': dados.get('contratado', {}).get('cpf', ''),
        '{{CONTRATADO_RG}}': dados.get('contratado', {}).get('rg', ''),
        '{{CONTRATADO_ENDERECO}}': dados.get('contratado', {}).get('endereco', ''),
        '{{CONTRATADO_TELEFONE}}': dados.get('contratado', {}).get('telefone', ''),
        '{{CONTRATADO_EMAIL}}': dados.get('contratado', {}).get('email', ''),
        '{{CONTRATADO_PROFISSAO}}': dados.get('contratado', {}).get('profissao', ''),
        
        '{{DATA_INICIO}}': dados.get('contrato', {}).get('data_inicio', ''),
        '{{DATA_FIM}}': dados.get('contrato', {}).get('data_fim', ''),
        '{{VALOR}}': dados.get('contrato', {}).get('valor', ''),
        '{{DESCRICAO_SERVICO}}': dados.get('contrato', {}).get('descricao_servico', ''),
        '{{FORMA_PAGAMENTO}}': dados.get('contrato', {}).get('forma_pagamento', ''),
        '{{CLAUSULAS_ESPECIAIS}}': dados.get('contrato', {}).get('clausulas_especiais', ''),
        
        '{{DATA_ATUAL}}': datetime.now().strftime('%d/%m/%Y'),
        '{{HORA_ATUAL}}': datetime.now().strftime('%H:%M:%S'),
    }
    
    # Substituir todos os placeholders
    for placeholder, valor in placeholders.items():
        conteudo = conteudo.replace(placeholder, str(valor))
    
    return conteudo

