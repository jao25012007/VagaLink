import os
import json
import time
from functools import wraps
from flask import Flask, request, jsonify, render_template 
from flask_cors import CORS
from google import genai
from google.genai import types
from google.genai.errors import APIError

# --- Configuração Inicial ---
app = Flask(__name__)
CORS(app) 

# Nome da variável de ambiente que contém sua chave API
API_KEY_NAME = "GEMINI_API_KEY"
MODEL_NAME = "gemini-2.5-flash" 

# --- SIMULAÇÃO DE BANCO DE DADOS (Substituir por um DB real em produção) ---

# Tabela de Hospitais (Clientes)
hospitais_db = {
    "hospital_a": {"id": "hospital_a", "nome": "Hospital Alpha Clínicas"},
    "hospital_b": {"id": "hospital_b", "nome": "Maringá Saúde"},
}

# Tabela de Médicos (Usuários)
# Senhas de teste: '123' ou '456'
medicos_db = {
    "hospital_a-12345/SP": {"nome": "Dra. Ana Silva", "hospital_id": "hospital_a", "senha": "123"},
    "hospital_a-dr.carlos@alpha.com": {"nome": "Dr. Carlos Mendes", "hospital_id": "hospital_a", "senha": "456"},
    "hospital_b-99887/PR": {"nome": "Dr. João Pereira", "hospital_id": "hospital_b", "senha": "123"},
}

# Tabela de Pacientes (Temporária por sessão/ID)
# Formato: { 'paciente_id': {dados_do_paciente} }
pacientes_db = {}
proximo_paciente_id = 1

# --- Esquema de Saída JSON (força a IA a seguir este formato) ---
JSON_SCHEMA = types.Schema(
    type=types.Type.OBJECT,
    properties={
        "doenca_principal": types.Schema(
            type=types.Type.STRING,
            description="O diagnóstico provisório mais provável em markdown com pontuação de certeza de 1 a 100."
        ),
        "diagnostico_diferencial": types.Schema(
            type=types.Type.STRING,
            description="Uma lista de 3 a 5 outras doenças possíveis, formatadas em markdown, e os critérios para descartá-las."
        ),
        "tratamento_recomendado": types.Schema(
            type=types.Type.STRING,
            description="Lista de ações de triagem (exames, internação) e tratamento inicial em markdown, começando com 'Ações Imediatas: '."
        )
    },
    required=["doenca_principal", "diagnostico_diferencial", "tratamento_recomendado"]
)


# --- Funções de Utilitário e Cliente Gemini ---

def get_gemini_client():
    """Função para obter o cliente Gemini, verificando a chave API."""
    api_key = os.getenv(API_KEY_NAME)
    if not api_key:
        raise ValueError(f"Chave API não encontrada. Por favor, defina a variável de ambiente '{API_KEY_NAME}' no seu terminal.")
    return genai.Client(api_key=api_key)

def retry_on_api_error(max_tries=3, delay_seconds=2):
    """Decorador de Retry (Tentativas) para lidar com erros de comunicação de forma robusta."""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            tries = 0
            while tries < max_tries:
                try:
                    return func(*args, **kwargs)
                except APIError as e:
                    tries += 1
                    if tries >= max_tries:
                        raise e
                    print(f"Tentativa {tries}/{max_tries} falhou com APIError: {e}. Re-tentando em {delay_seconds} segundos...")
                    time.sleep(delay_seconds)
            return None 
        return wrapper
    return decorator


# --- Rotas da API ---

@app.route('/')
def serve_frontend():
    """Serve o arquivo index.html (ou o conteúdo dele) para o usuário."""
    return "O frontend (index.html) deve ser aberto diretamente no navegador. As rotas Flask são apenas APIs."

@app.route('/login', methods=['POST'])
def login():
    """Rota para simular o login de um médico."""
    dados = request.get_json()
    hospital_id = dados.get('hospital_id')
    email_crm = dados.get('email_crm')
    password = dados.get('password')

    if not hospital_id or not email_crm or not password:
        return jsonify({"erro": "Dados de login incompletos."}), 400

    chave_medico = f"{hospital_id}-{email_crm}"
    medico = medicos_db.get(chave_medico)
    hospital = hospitais_db.get(hospital_id)

    if not medico or medico['senha'] != password:
        return jsonify({"erro": "Credenciais inválidas ou hospital/CRM incorreto."}), 401
    
    return jsonify({
        "mensagem": "Login bem-sucedido",
        "medico_nome": medico['nome'],
        "hospital_nome": hospital['nome'],
        "hospital_id": hospital_id
    }), 200

@app.route('/salvar_paciente', methods=['POST'])
def salvar_paciente():
    """Rota para simular o salvamento dos dados de um novo paciente."""
    global pacientes_db, proximo_paciente_id
    dados = request.get_json()

    # Validação básica
    if not all(k in dados for k in ['nome', 'idade', 'altura', 'peso', 'sexo', 'hospital_id']):
        return jsonify({"erro": "Dados do paciente incompletos."}), 400

    # Cria o registro do paciente
    paciente = {
        'id': proximo_paciente_id,
        'nome': dados['nome'],
        'idade': int(dados['idade']),
        'altura': float(dados['altura']),
        'peso': float(dados['peso']),
        'sexo': dados['sexo'],
        'hospital_id': dados['hospital_id'] # Associa o paciente ao hospital
    }

    pacientes_db[proximo_paciente_id] = paciente
    proximo_paciente_id += 1

    return jsonify({"mensagem": "Paciente salvo com sucesso.", "paciente": paciente}), 200


@app.route('/diagnostico_ia', methods=['POST'])
@retry_on_api_error()
def diagnostico_ia():
    """Rota principal: Envia dados do paciente e sintomas para a IA e retorna o diagnóstico."""
    try:
        dados = request.get_json()
        paciente_id = dados.get('paciente_id')
        sintomas = dados.get('sintomas', [])
        hospital_id_request = dados.get('hospital_id')

        # 1. Validação
        if not paciente_id or not sintomas:
            return jsonify({"erro": "ID do paciente ou sintomas não fornecidos."}), 400
        
        paciente = pacientes_db.get(paciente_id)
        if not paciente or paciente.get('hospital_id') != hospital_id_request:
             return jsonify({"erro": "Paciente não encontrado ou ID do hospital não confere."}), 404

        client = get_gemini_client()

        # 2. Criação do Prompt
        sintomas_str = "\n".join([f"- {s}" for s in sintomas])
        
        prompt = f"""
        Você é um sistema de triagem de Inteligência Artificial para médicos de emergência. Sua função é analisar 
        o quadro clínico do paciente e sugerir, de forma **estritamente técnica e rápida**, os diagnósticos mais prováveis 
        (em português), diferenciais e o tratamento/próxima ação de triagem recomendado.

        **Dados do Paciente:**
        - Nome: {paciente['nome']}
        - Idade: {paciente['idade']} anos
        - Sexo: {paciente['sexo']}
        - IMC: {(paciente['peso'] / (paciente['altura']**2)):.2f} ({paciente['peso']}kg / {paciente['altura']}m)

        **Sintomas Relatados:**
        {sintomas_str}

        Com base nos dados acima e no seu conhecimento médico, gere a resposta no formato JSON estrito conforme o esquema fornecido.
        Sua resposta deve ser concisa, focar apenas na saída JSON e não deve incluir comentários ou texto extra.
        """
        
        # 3. Chamada ao Modelo Generativo
        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=prompt,
            config=types.GenerateContentConfig(
                # Garante que a saída é JSON
                response_mime_type="application/json",
                response_schema=JSON_SCHEMA, # Usa o esquema JSON_SCHEMA
                # LINHA DE CONFLITO REMOVIDA: tools=[{"google_search": {}}],
            ),
        )

        # 4. Extração e Validação do JSON
        json_text = response.text.strip()
        
        # CORREÇÃO CRÍTICA (mantida): Remove blocos de código markdown que o modelo pode adicionar.
        if json_text.startswith("```json"):
            json_text = json_text[len("```json"):].rstrip("```").strip()
        elif json_text.startswith("```"):
             json_text = json_text[len("```"):].rstrip("```").strip()

        try:
            # Tenta carregar a string JSON
            diagnostico_data = json.loads(json_text)
        except json.JSONDecodeError:
            # Se falhar, é um erro do modelo que não retornou JSON válido.
            print(f"ERRO DE PARSING JSON: Modelo retornou texto inválido: {json_text}")
            raise ValueError(f"Modelo não retornou JSON válido após limpeza: {json_text}")


        # 5. Adiciona dados do paciente e sintomas para o retorno
        diagnostico_data['paciente'] = paciente
        diagnostico_data['sintomas_relatados'] = sintomas

        # Captura fontes (agora sempre vazio pois a ferramenta foi removida)
        sources = []
        if response.candidates and response.candidates[0].grounding_metadata:
            for attribution in response.candidates[0].grounding_metadata.grounding_attributions:
                if hasattr(attribution, 'web') and attribution.web:
                     sources.append({
                        "uri": attribution.web.uri,
                        "title": attribution.web.title
                    })
                
        return jsonify({"diagnostico": diagnostico_data, "fontes": sources}), 200

    except ValueError as e:
        return jsonify({"erro": f"Erro de validação, chave API ou parsing JSON: {e}"}), 400
    except APIError as e:
        # Captura erros de comunicação com o servidor Gemini
        print(f"ERRO API GENAI: {e}")
        return jsonify({"erro": f"Falha na comunicação com o Gemini. Detalhes: {e}"}), 400
    except Exception as e:
        # Captura outros erros inesperados
        print(f"ERRO CRÍTICO: {e}")
        return jsonify({"erro": f"Erro inesperado ao gerar diagnóstico: {e}"}), 500


# --- Inicialização da Aplicação ---

if __name__ == '__main__':
    if not os.getenv(API_KEY_NAME):
        print(f"\n!!! AVISO CRÍTICO !!!")
        print(f"A variável de ambiente '{API_KEY_NAME}' NÃO ESTÁ DEFINIDA.")
        print(f"A aplicação NÃO CONSEGUIRÁ USAR a IA de diagnóstico.")
        print(f"Exemplo de como definir no terminal (substitua a chave):")
        print(f"set {API_KEY_NAME}=SUA_CHAVE_AQUI (Windows)")
        print(f"export {API_KEY_NAME}=SUA_CHAVE_AQUI (Linux/MacOS)\n")
    
    # Executa a aplicação Flask
    app.run(debug=True)
