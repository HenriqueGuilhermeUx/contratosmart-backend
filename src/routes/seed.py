from flask import Blueprint, request, jsonify
from src.models.user import db, ContractType, ContractTemplate

seed_bp = Blueprint('seed', __name__)

@seed_bp.route('/seed-data', methods=['POST'])
def seed_initial_data():
    """Popula o banco com dados iniciais"""
    try:
        # Verificar se já existem dados
        if ContractType.query.count() > 0:
            return jsonify({
                'success': True,
                'message': 'Dados já existem no banco'
            })

        # Criar tipos de contratos
        contract_types_data = [
            {
                'nome': 'Contrato de Prestação de Serviços Gerais',
                'descricao': 'Modelo padrão para prestação de serviços diversos',
                'categoria': 'servico'
            },
            {
                'nome': 'Contrato de Namoro',
                'descricao': 'Acordo de relacionamento amoroso com termos específicos',
                'categoria': 'namoro'
            },
            {
                'nome': 'Contrato de Cuidador de Pets',
                'descricao': 'Acordo para cuidados de animais de estimação',
                'categoria': 'pets'
            },
            {
                'nome': 'Contrato de Pintura Residencial',
                'descricao': 'Serviços de pintura para residências',
                'categoria': 'servico'
            },
            {
                'nome': 'Contrato de Serviços de Pedreiro',
                'descricao': 'Serviços de construção e reforma',
                'categoria': 'servico'
            },
            {
                'nome': 'Contrato de Serviços Elétricos',
                'descricao': 'Instalações e manutenções elétricas',
                'categoria': 'servico'
            },
            {
                'nome': 'Contrato de Aluguel Residencial',
                'descricao': 'Locação de imóveis residenciais',
                'categoria': 'aluguel'
            }
        ]

        contract_types = []
        for ct_data in contract_types_data:
            ct = ContractType(**ct_data)
            db.session.add(ct)
            contract_types.append(ct)

        db.session.flush()  # Para obter os IDs

        # Criar templates
        templates_data = [
            {
                'contract_type_id': contract_types[0].id,  # Prestação de Serviços Gerais
                'nome': 'Template Padrão - Prestação de Serviços',
                'conteudo_template': get_template_prestacao_servicos(),
                'campos_obrigatorios': '{"contratante": ["nome_completo", "cpf", "endereco"], "contratado": ["nome_completo", "cpf", "profissao"], "contrato": ["data_inicio", "valor", "descricao_servico"]}',
                'campos_opcionais': '{"contratante": ["rg", "telefone", "email"], "contratado": ["rg", "telefone", "email", "endereco"], "contrato": ["data_fim", "forma_pagamento", "clausulas_especiais"]}'
            },
            {
                'contract_type_id': contract_types[1].id,  # Namoro
                'nome': 'Template Padrão - Contrato de Namoro',
                'conteudo_template': get_template_namoro(),
                'campos_obrigatorios': '{"contratante": ["nome_completo", "cpf"], "contratado": ["nome_completo", "cpf"], "contrato": ["data_inicio"]}',
                'campos_opcionais': '{"contratante": ["rg", "telefone", "email", "endereco"], "contratado": ["rg", "telefone", "email", "endereco"], "contrato": ["data_fim", "clausulas_especiais"]}'
            },
            {
                'contract_type_id': contract_types[2].id,  # Cuidador de Pets
                'nome': 'Template Padrão - Cuidador de Pets',
                'conteudo_template': get_template_cuidador_pets(),
                'campos_obrigatorios': '{"contratante": ["nome_completo", "cpf", "endereco"], "contratado": ["nome_completo", "cpf"], "contrato": ["data_inicio", "valor", "descricao_servico"]}',
                'campos_opcionais': '{"contratante": ["rg", "telefone", "email"], "contratado": ["rg", "telefone", "email", "endereco"], "contrato": ["data_fim", "forma_pagamento", "clausulas_especiais"]}'
            },
            {
                'contract_type_id': contract_types[3].id,  # Pintura
                'nome': 'Template Padrão - Pintura Residencial',
                'conteudo_template': get_template_pintura(),
                'campos_obrigatorios': '{"contratante": ["nome_completo", "cpf", "endereco"], "contratado": ["nome_completo", "cpf", "profissao"], "contrato": ["data_inicio", "valor", "descricao_servico"]}',
                'campos_opcionais': '{"contratante": ["rg", "telefone", "email"], "contratado": ["rg", "telefone", "email", "endereco"], "contrato": ["data_fim", "forma_pagamento", "clausulas_especiais"]}'
            }
        ]

        for template_data in templates_data:
            template = ContractTemplate(**template_data)
            db.session.add(template)

        db.session.commit()

        return jsonify({
            'success': True,
            'message': 'Dados iniciais criados com sucesso',
            'data': {
                'contract_types': len(contract_types_data),
                'templates': len(templates_data)
            }
        })

    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

def get_template_prestacao_servicos():
    return """
CONTRATO DE PRESTAÇÃO DE SERVIÇOS

Pelo presente instrumento particular, as partes abaixo qualificadas:

CONTRATANTE: {{CONTRATANTE_NOME}}, portador do CPF nº {{CONTRATANTE_CPF}}, RG nº {{CONTRATANTE_RG}}, residente e domiciliado em {{CONTRATANTE_ENDERECO}}, telefone {{CONTRATANTE_TELEFONE}}, e-mail {{CONTRATANTE_EMAIL}}.

CONTRATADO: {{CONTRATADO_NOME}}, portador do CPF nº {{CONTRATADO_CPF}}, RG nº {{CONTRATADO_RG}}, profissão {{CONTRATADO_PROFISSAO}}, residente e domiciliado em {{CONTRATADO_ENDERECO}}, telefone {{CONTRATADO_TELEFONE}}, e-mail {{CONTRATADO_EMAIL}}.

Têm entre si justo e acordado o presente contrato de prestação de serviços, que se regerá pelas cláusulas seguintes:

CLÁUSULA 1ª - DO OBJETO
O presente contrato tem por objeto a prestação dos seguintes serviços: {{DESCRICAO_SERVICO}}.

CLÁUSULA 2ª - DO PRAZO
Os serviços deverão ser iniciados em {{DATA_INICIO}} e concluídos até {{DATA_FIM}}.

CLÁUSULA 3ª - DO VALOR E FORMA DE PAGAMENTO
Pelo serviço prestado, o CONTRATANTE pagará ao CONTRATADO o valor total de {{VALOR}}.
Forma de pagamento: {{FORMA_PAGAMENTO}}.

CLÁUSULA 4ª - DAS OBRIGAÇÕES DO CONTRATADO
O CONTRATADO obriga-se a:
a) Executar os serviços com qualidade e dentro do prazo estabelecido;
b) Utilizar materiais de boa qualidade;
c) Responsabilizar-se por eventuais danos causados por negligência.

CLÁUSULA 5ª - DAS OBRIGAÇÕES DO CONTRATANTE
O CONTRATANTE obriga-se a:
a) Efetuar o pagamento conforme acordado;
b) Fornecer as condições necessárias para a execução dos serviços;
c) Comunicar imediatamente qualquer irregularidade.

CLÁUSULA 6ª - CLÁUSULAS ESPECIAIS
{{CLAUSULAS_ESPECIAIS}}

CLÁUSULA 7ª - DO FORO
Fica eleito o foro da comarca de [CIDADE], para dirimir quaisquer questões oriundas do presente contrato.

E por estarem assim justos e contratados, firmam o presente instrumento em duas vias de igual teor e forma.

Local e data: ________________, {{DATA_ATUAL}}

_________________________                    _________________________
{{CONTRATANTE_NOME}}                         {{CONTRATADO_NOME}}
CONTRATANTE                                  CONTRATADO
"""

def get_template_namoro():
    return """
CONTRATO DE NAMORO

Pelo presente instrumento particular, as partes abaixo qualificadas:

PRIMEIRA PARTE: {{CONTRATANTE_NOME}}, portador do CPF nº {{CONTRATANTE_CPF}}, RG nº {{CONTRATANTE_RG}}, residente e domiciliado em {{CONTRATANTE_ENDERECO}}, telefone {{CONTRATANTE_TELEFONE}}, e-mail {{CONTRATANTE_EMAIL}}.

SEGUNDA PARTE: {{CONTRATADO_NOME}}, portador do CPF nº {{CONTRATADO_CPF}}, RG nº {{CONTRATADO_RG}}, residente e domiciliado em {{CONTRATADO_ENDERECO}}, telefone {{CONTRATADO_TELEFONE}}, e-mail {{CONTRATADO_EMAIL}}.

Têm entre si justo e acordado o presente contrato de namoro, que se regerá pelas cláusulas seguintes:

CLÁUSULA 1ª - DO OBJETO
O presente contrato tem por objeto estabelecer as regras e condições do relacionamento amoroso entre as partes.

CLÁUSULA 2ª - DO INÍCIO DO RELACIONAMENTO
O relacionamento teve início em {{DATA_INICIO}}.

CLÁUSULA 3ª - DOS DIREITOS E DEVERES
As partes comprometem-se a:
a) Manter fidelidade mútua;
b) Respeitar a individualidade do parceiro;
c) Comunicar-se de forma clara e honesta;
d) Apoiar-se mutuamente nos momentos difíceis.

CLÁUSULA 4ª - DA DURAÇÃO
Este contrato vigorará por prazo indeterminado, podendo ser rescindido por qualquer das partes mediante comunicação prévia.

CLÁUSULA 5ª - CLÁUSULAS ESPECIAIS
{{CLAUSULAS_ESPECIAIS}}

CLÁUSULA 6ª - DA RESCISÃO
O presente contrato poderá ser rescindido:
a) Por mútuo acordo;
b) Por iniciativa de qualquer das partes;
c) Por descumprimento das cláusulas estabelecidas.

E por estarem assim justos e contratados, firmam o presente instrumento em duas vias de igual teor e forma.

Local e data: ________________, {{DATA_ATUAL}}

_________________________                    _________________________
{{CONTRATANTE_NOME}}                         {{CONTRATADO_NOME}}
PRIMEIRA PARTE                               SEGUNDA PARTE
"""

def get_template_cuidador_pets():
    return """
CONTRATO DE PRESTAÇÃO DE SERVIÇOS - CUIDADOR DE PETS

Pelo presente instrumento particular, as partes abaixo qualificadas:

CONTRATANTE: {{CONTRATANTE_NOME}}, portador do CPF nº {{CONTRATANTE_CPF}}, RG nº {{CONTRATANTE_RG}}, residente e domiciliado em {{CONTRATANTE_ENDERECO}}, telefone {{CONTRATANTE_TELEFONE}}, e-mail {{CONTRATANTE_EMAIL}}.

CONTRATADO: {{CONTRATADO_NOME}}, portador do CPF nº {{CONTRATADO_CPF}}, RG nº {{CONTRATADO_RG}}, residente e domiciliado em {{CONTRATADO_ENDERECO}}, telefone {{CONTRATADO_TELEFONE}}, e-mail {{CONTRATADO_EMAIL}}.

Têm entre si justo e acordado o presente contrato de prestação de serviços de cuidador de pets, que se regerá pelas cláusulas seguintes:

CLÁUSULA 1ª - DO OBJETO
O presente contrato tem por objeto a prestação de serviços de cuidados com animais de estimação, conforme especificado: {{DESCRICAO_SERVICO}}.

CLÁUSULA 2ª - DO PRAZO
Os serviços deverão ser prestados no período de {{DATA_INICIO}} até {{DATA_FIM}}.

CLÁUSULA 3ª - DO VALOR E FORMA DE PAGAMENTO
Pelo serviço prestado, o CONTRATANTE pagará ao CONTRATADO o valor total de {{VALOR}}.
Forma de pagamento: {{FORMA_PAGAMENTO}}.

CLÁUSULA 4ª - DAS OBRIGAÇÕES DO CONTRATADO
O CONTRATADO obriga-se a:
a) Cuidar do(s) animal(is) com carinho e responsabilidade;
b) Seguir rigorosamente as instruções de alimentação e medicação;
c) Manter o animal em ambiente seguro e limpo;
d) Comunicar imediatamente qualquer emergência ou problema de saúde;
e) Não permitir que terceiros tenham acesso ao animal sem autorização.

CLÁUSULA 5ª - DAS OBRIGAÇÕES DO CONTRATANTE
O CONTRATANTE obriga-se a:
a) Fornecer todas as informações necessárias sobre o animal;
b) Disponibilizar ração, medicamentos e acessórios necessários;
c) Informar contatos de emergência e veterinário de confiança;
d) Efetuar o pagamento conforme acordado.

CLÁUSULA 6ª - DA RESPONSABILIDADE
O CONTRATADO responsabiliza-se pelos cuidados do animal durante o período contratado, exceto em casos de força maior ou problemas de saúde preexistentes.

CLÁUSULA 7ª - CLÁUSULAS ESPECIAIS
{{CLAUSULAS_ESPECIAIS}}

E por estarem assim justos e contratados, firmam o presente instrumento em duas vias de igual teor e forma.

Local e data: ________________, {{DATA_ATUAL}}

_________________________                    _________________________
{{CONTRATANTE_NOME}}                         {{CONTRATADO_NOME}}
CONTRATANTE                                  CONTRATADO
"""

def get_template_pintura():
    return """
CONTRATO DE PRESTAÇÃO DE SERVIÇOS - PINTURA RESIDENCIAL

Pelo presente instrumento particular, as partes abaixo qualificadas:

CONTRATANTE: {{CONTRATANTE_NOME}}, portador do CPF nº {{CONTRATANTE_CPF}}, RG nº {{CONTRATANTE_RG}}, residente e domiciliado em {{CONTRATANTE_ENDERECO}}, telefone {{CONTRATANTE_TELEFONE}}, e-mail {{CONTRATANTE_EMAIL}}.

CONTRATADO: {{CONTRATADO_NOME}}, portador do CPF nº {{CONTRATADO_CPF}}, RG nº {{CONTRATADO_RG}}, profissão {{CONTRATADO_PROFISSAO}}, residente e domiciliado em {{CONTRATADO_ENDERECO}}, telefone {{CONTRATADO_TELEFONE}}, e-mail {{CONTRATADO_EMAIL}}.

Têm entre si justo e acordado o presente contrato de prestação de serviços de pintura, que se regerá pelas cláusulas seguintes:

CLÁUSULA 1ª - DO OBJETO
O presente contrato tem por objeto a prestação de serviços de pintura residencial, conforme especificado: {{DESCRICAO_SERVICO}}.

CLÁUSULA 2ª - DO PRAZO
Os serviços deverão ser iniciados em {{DATA_INICIO}} e concluídos até {{DATA_FIM}}.

CLÁUSULA 3ª - DO VALOR E FORMA DE PAGAMENTO
Pelo serviço prestado, o CONTRATANTE pagará ao CONTRATADO o valor total de {{VALOR}}.
Forma de pagamento: {{FORMA_PAGAMENTO}}.

CLÁUSULA 4ª - DOS MATERIAIS
Os materiais necessários para a execução dos serviços serão fornecidos pelo CONTRATADO, já inclusos no valor do contrato, salvo especificação em contrário.

CLÁUSULA 5ª - DAS OBRIGAÇÕES DO CONTRATADO
O CONTRATADO obriga-se a:
a) Executar os serviços com qualidade profissional;
b) Utilizar materiais de primeira qualidade;
c) Proteger móveis e objetos durante a execução;
d) Limpar o local após a conclusão dos trabalhos;
e) Garantir o serviço por 6 (seis) meses contra defeitos de execução.

CLÁUSULA 6ª - DAS OBRIGAÇÕES DO CONTRATANTE
O CONTRATANTE obriga-se a:
a) Permitir livre acesso ao local dos serviços;
b) Fornecer energia elétrica e água necessárias;
c) Efetuar o pagamento conforme acordado;
d) Retirar ou proteger objetos de valor.

CLÁUSULA 7ª - CLÁUSULAS ESPECIAIS
{{CLAUSULAS_ESPECIAIS}}

CLÁUSULA 8ª - DA GARANTIA
O CONTRATADO garante o serviço executado pelo prazo de 6 (seis) meses contra defeitos de execução, excluindo-se desgaste natural e danos causados pelo uso inadequado.

E por estarem assim justos e contratados, firmam o presente instrumento em duas vias de igual teor e forma.

Local e data: ________________, {{DATA_ATUAL}}

_________________________                    _________________________
{{CONTRATANTE_NOME}}                         {{CONTRATADO_NOME}}
CONTRATANTE                                  CONTRATADO
"""

