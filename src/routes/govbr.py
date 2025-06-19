from flask import Blueprint, request, jsonify, redirect, url_for, session
import requests
import json
import os
import base64
import hashlib
import time
from urllib.parse import urlencode
from src.models.user import db, DigitalSignature

govbr_bp = Blueprint('govbr', __name__)

# Configurações da API Gov.br
# Em produção, estas configurações devem vir de variáveis de ambiente ou arquivo de configuração seguro
GOVBR_CLIENT_ID = "seu-client-id"
GOVBR_CLIENT_SECRET = "seu-client-secret"
GOVBR_REDIRECT_URI = "http://localhost:5000/api/govbr/callback"
GOVBR_AUTH_URL = "https://sso.staging.acesso.gov.br/authorize"
GOVBR_TOKEN_URL = "https://sso.staging.acesso.gov.br/token"
GOVBR_USERINFO_URL = "https://sso.staging.acesso.gov.br/userinfo"
GOVBR_CERTIFICATES_URL = "https://assinatura-api.staging.iti.br/externo/v2/certificados"
GOVBR_SIGNATURE_URL = "https://assinatura-api.staging.iti.br/externo/v2/assinar"

@govbr_bp.route('/auth', methods=['GET'])
def auth():
    """Inicia o fluxo de autenticação com o Gov.br"""
    # Parâmetros para a URL de autorização
    params = {
        'response_type': 'code',
        'client_id': GOVBR_CLIENT_ID,
        'scope': 'openid email profile govbr_confiabilidades',
        'redirect_uri': GOVBR_REDIRECT_URI,
        'state': generate_state(),
        'nonce': generate_nonce()
    }
    
    # Armazenar state e nonce para validação posterior
    session['govbr_state'] = params['state']
    session['govbr_nonce'] = params['nonce']
    
    # Construir a URL de autorização
    auth_url = f"{GOVBR_AUTH_URL}?{urlencode(params)}"
    
    return jsonify({
        'success': True,
        'auth_url': auth_url
    })

@govbr_bp.route('/callback', methods=['GET'])
def callback():
    """Callback para receber o código de autorização do Gov.br"""
    # Obter o código de autorização e state da URL
    code = request.args.get('code')
    state = request.args.get('state')
    
    # Verificar se o state corresponde ao que foi enviado
    if state != session.get('govbr_state'):
        return jsonify({
            'success': False,
            'error': 'Invalid state parameter'
        }), 400
    
    # Trocar o código por um token de acesso
    token_response = exchange_code_for_token(code)
    
    if not token_response.get('success'):
        return jsonify(token_response), 400
    
    # Obter informações do usuário
    userinfo_response = get_user_info(token_response['access_token'])
    
    if not userinfo_response.get('success'):
        return jsonify(userinfo_response), 400
    
    # Armazenar o token e informações do usuário na sessão
    session['govbr_access_token'] = token_response['access_token']
    session['govbr_id_token'] = token_response['id_token']
    session['govbr_userinfo'] = userinfo_response['userinfo']
    
    # Redirecionar para a página de assinatura
    # Em uma aplicação real, você redirecionaria para a página de assinatura no frontend
    return jsonify({
        'success': True,
        'message': 'Autenticação com Gov.br realizada com sucesso',
        'userinfo': userinfo_response['userinfo']
    })

@govbr_bp.route('/userinfo', methods=['GET'])
def userinfo():
    """Retorna as informações do usuário autenticado"""
    if 'govbr_userinfo' not in session:
        return jsonify({
            'success': False,
            'error': 'User not authenticated with Gov.br'
        }), 401
    
    return jsonify({
        'success': True,
        'userinfo': session['govbr_userinfo']
    })

@govbr_bp.route('/certificates', methods=['GET'])
def certificates():
    """Obtém os certificados disponíveis para o usuário"""
    if 'govbr_access_token' not in session:
        return jsonify({
            'success': False,
            'error': 'User not authenticated with Gov.br'
        }), 401
    
    try:
        response = requests.get(
            GOVBR_CERTIFICATES_URL,
            headers={
                'Authorization': f"Bearer {session['govbr_access_token']}",
                'Content-Type': 'application/json'
            }
        )
        
        if response.status_code != 200:
            return jsonify({
                'success': False,
                'error': f'Failed to get certificates: {response.text}'
            }), response.status_code
        
        certificates = response.json()
        
        return jsonify({
            'success': True,
            'certificates': certificates
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@govbr_bp.route('/sign', methods=['POST'])
def sign():
    """Assina um documento usando a API do Gov.br"""
    if 'govbr_access_token' not in session:
        return jsonify({
            'success': False,
            'error': 'User not authenticated with Gov.br'
        }), 401
    
    try:
        data = request.get_json()
        
        # Validação básica
        required_fields = ['contract_id', 'user_id', 'hash_documento', 'certificate_id']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'success': False,
                    'error': f'Campo obrigatório ausente: {field}'
                }), 400
        
        # Preparar os dados para a assinatura
        signature_data = {
            'hashBase64': base64.b64encode(data['hash_documento'].encode()).decode(),
            'certificateId': data['certificate_id']
        }
        
        # Fazer a requisição para a API de assinatura
        response = requests.post(
            GOVBR_SIGNATURE_URL,
            headers={
                'Authorization': f"Bearer {session['govbr_access_token']}",
                'Content-Type': 'application/json'
            },
            json=signature_data
        )
        
        if response.status_code != 200:
            return jsonify({
                'success': False,
                'error': f'Failed to sign document: {response.text}'
            }), response.status_code
        
        signature_result = response.json()
        
        # Salvar a assinatura no banco de dados
        digital_signature = DigitalSignature(
            contract_id=data['contract_id'],
            user_id=data['user_id'],
            tipo_assinatura='govbr',
            hash_assinatura=signature_result.get('signature'),
            timestamp_assinatura=time.time(),
            ip_address=request.remote_addr,
            user_agent=request.user_agent.string,
            status='assinado'
        )
        
        # Armazenar informações do certificado
        certificate_info = {
            'certificate_id': data['certificate_id'],
            'govbr_user_info': session.get('govbr_userinfo'),
            'signature_info': signature_result
        }
        digital_signature.set_certificado_info(certificate_info)
        
        db.session.add(digital_signature)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Documento assinado com sucesso',
            'signature': signature_result
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

def exchange_code_for_token(code):
    """Troca o código de autorização por um token de acesso"""
    try:
        # Preparar os dados para a requisição
        token_data = {
            'grant_type': 'authorization_code',
            'code': code,
            'redirect_uri': GOVBR_REDIRECT_URI
        }
        
        # Preparar a autenticação (Basic Auth)
        auth = base64.b64encode(f"{GOVBR_CLIENT_ID}:{GOVBR_CLIENT_SECRET}".encode()).decode()
        
        # Fazer a requisição para obter o token
        response = requests.post(
            GOVBR_TOKEN_URL,
            headers={
                'Authorization': f"Basic {auth}",
                'Content-Type': 'application/x-www-form-urlencoded'
            },
            data=token_data
        )
        
        if response.status_code != 200:
            return {
                'success': False,
                'error': f'Failed to exchange code for token: {response.text}'
            }
        
        token_response = response.json()
        
        return {
            'success': True,
            'access_token': token_response['access_token'],
            'id_token': token_response.get('id_token'),
            'token_type': token_response['token_type'],
            'expires_in': token_response['expires_in']
        }
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }

def get_user_info(access_token):
    """Obtém informações do usuário usando o token de acesso"""
    try:
        response = requests.get(
            GOVBR_USERINFO_URL,
            headers={
                'Authorization': f"Bearer {access_token}"
            }
        )
        
        if response.status_code != 200:
            return {
                'success': False,
                'error': f'Failed to get user info: {response.text}'
            }
        
        userinfo = response.json()
        
        return {
            'success': True,
            'userinfo': userinfo
        }
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }

def generate_state():
    """Gera um valor state aleatório para proteção contra CSRF"""
    return hashlib.sha256(os.urandom(32)).hexdigest()

def generate_nonce():
    """Gera um valor nonce aleatório para proteção contra replay attacks"""
    return hashlib.sha256(os.urandom(32)).hexdigest()

