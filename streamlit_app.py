import streamlit as st
import google.generativeai as genai
import requests
import re
import os

def get_secret(key, default=""):
    try:
        # Tenta do Streamlit secrets (Cloud)
        if hasattr(st, 'secrets') and key in st.secrets:
            return st.secrets[key]
    except:
        pass
    
    try:
        # Tenta de variáveis de ambiente
        return os.environ[key]
    except KeyError:
        # Fallback para valor padrão ou vazio
        return default

# Obtém configurações
GEMINI_API_KEY = get_secret("GEMINI_API_KEY")
GOOGLE_DOCS_URL = get_secret("GOOGLE_DOCS_URL")

# =========================================================

@st.cache_data(ttl=3600, show_spinner=False)
def load_document():
    """Carrega o documento do Google Docs com cache de 1 hora"""
    try:
        if not GOOGLE_DOCS_URL:
            st.error("URL do documento não configurado.")
            return None
            
        if '/document/d/' in GOOGLE_DOCS_URL:
            doc_id = re.search(r'/document/d/([a-zA-Z0-9-_]+)', GOOGLE_DOCS_URL).group(1)
            export_url = f"https://docs.google.com/document/d/{doc_id}/export?format=txt"
            
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
            response = requests.get(export_url, headers=headers, timeout=30)
            response.encoding = 'utf-8'
            response.raise_for_status()
            
            return response.text
    except Exception as e:
        st.error(f"Erro ao carregar documento: {str(e)}")
        return None
    return None

def setup_gemini():
    try:
        if not GEMINI_API_KEY:
            st.error("Chave da API Gemini não configurada.")
            return None
            
        genai.configure(api_key=GEMINI_API_KEY)
        return genai.GenerativeModel("gemini-2.5-flash-lite")
    except Exception as e:
        st.error(f"Erro ao configurar Gemini: {str(e)}")
        return None

st.set_page_config(
    page_title="John Wiki - Seu especialista accountfy",
    page_icon="🙅‍♂️",
    layout="centered",
    initial_sidebar_state="collapsed"
)

st.markdown("""
<style>
    .main { background-color: #0E1117; color: #FFFFFF; padding: 2rem; }
    .stChatInput { background-color: #0E1117; }
    .stTextInput textarea { 
        background-color: #1E1E1E !important; color: #FFFFFF !important; 
        border: 1px solid #4A4A4A !important; border-radius: 15px !important; padding: 15px !important; 
    }
    .stTextInput textarea:focus { border-color: #4e89e8 !important; box-shadow: 0 0 0 1px #4e89e8 !important; }
    .assistant-response { 
        background-color: #1E1E1E; color: #FFFFFF; padding: 20px; border-radius: 15px; 
        border-left: 4px solid #4e89e8; margin: 20px 0; box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    .user-question {
        background-color: #2D2D2D; color: #FFFFFF; padding: 20px; border-radius: 15px; margin: 20px 0;
        border-left: 4px solid #FF4B4B; box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    .header { text-align: center; margin-bottom: 40px; color: #FFFFFF; }
    .header h1 { color: #4e89e8 !important; font-weight: bold; margin-bottom: 10px; }
    .header p { color: #CCCCCC !important; font-size: 1.1em; }
    .stButton button {
        background-color: #4e89e8 !important; color: white !important; border: none !important;
        border-radius: 15px !important; padding: 12px 24px !important; font-weight: bold !important;
    }
    .stButton button:hover { background-color: #3a76d9 !important; }
    .stSpinner div { border-color: #4e89e8 transparent transparent transparent !important; }
    .footer { color: #888888 !important; font-size: 0.9em; text-align: center; margin-top: 30px; padding-top: 20px; border-top: 1px solid #2D2D2D; }
    .stMarkdown, .stText, .stAlert, .stSuccess, .stWarning, .stError { color: #FFFFFF !important; }
    .stTextInput textarea::placeholder { color: #888888 !important; }
    .config-error { 
        background-color: #2D2D2D; color: #FF6B6B; padding: 20px; border-radius: 10px; 
        border-left: 4px solid #FF4B4B; margin: 20px 0;
    }
</style>
""", unsafe_allow_html=True)

# Inicializar sessões
if "messages" not in st.session_state:
    st.session_state.messages = []

if "model" not in st.session_state:
    st.session_state.model = setup_gemini()
    st.session_state.document_text = load_document()

# Verificar se as configurações estão corretas
if not GEMINI_API_KEY or not GOOGLE_DOCS_URL:
    st.markdown("""
    <div class="config-error">
    <h3>⚠️ Configuração Necessária</h3>
    <p>Para usar o John Wiki, você precisa configurar:</p>
    <ol>
        <li><strong>GEMINI_API_KEY</strong> - Chave da API do Gemini</li>
        <li><strong>GOOGLE_DOCS_URL</strong> - URL do documento Google Docs</li>
    </ol>
    <p><strong>No Streamlit Cloud:</strong> Configure em Settings → Secrets</p>
    <p><strong>Localmente:</strong> Crie um arquivo .streamlit/secrets.toml</p>
    </div>
    """, unsafe_allow_html=True)
    st.stop()

if not st.session_state.model or not st.session_state.document_text:
    st.error("❌ Erro na configuração. Verifique se a chave API e o URL do documento estão corretos.")
    st.stop()

# Header
st.markdown('<div class="header">', unsafe_allow_html=True)
st.markdown('<h1>🙅‍♂️ John Wiki</h1>', unsafe_allow_html=True)
st.markdown('<p>Especialista Accountfy</p>', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# Histórico de mensagens
for message in st.session_state.messages:
    if message["role"] == "user":
        st.markdown(f'<div class="user-question"><strong style="color: #FF4B4B;">Você:</strong> <span style="color: #FFFFFF;">{message["content"]}</span></div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="assistant-response"><strong style="color: #4e89e8;">John Wiki:</strong> <span style="color: #FFFFFF;">{message["content"]}</span></div>', unsafe_allow_html=True)

# Input da pergunta
question = st.chat_input("Digite sua pergunta...")

if question:
    # Adicionar pergunta ao histórico
    st.session_state.messages.append({"role": "user", "content": question})
    
    st.markdown(
        f'<div class="user-question">'
        f'<strong style="color: #FF4B4B;">Você:</strong> '
        f'<span style="color: #FFFFFF;">{question}</span>'
        f'</div>', 
        unsafe_allow_html=True
    )

    # Gerar resposta
    with st.spinner("John Wiki está pensando..."):
        try:
            prompt = f"""
            Você é o John Wiki, um assistente de suporte especializado na Accountfy, em contabilidade e finanças. 
            Use EXCLUSIVAMENTE as informações do documento abaixo para responder, este documento contém informações
            sobre chamados encerrados e padrões de uso, analise cuidadosamente as informações e considere as soluções
            propostas nos comentários e em todo o documento para responder.

            DOCUMENTO:
            {st.session_state.document_text[:30000]}

            PERGUNTA: {question}

            RESPONDA:
            - De forma clara, simples, direta e útil, seja simpático 
            - Como um especialista contábil, mas não precisa declarar isso nem que é um especista, assistente, suporte, etc
            - Apenas com base no documento
            - Se não souber, diga educadamente, mas considere sinonimos e abreviações quando for analisar o documento, DF = Demonstração Financeira, B&F Budget & Forcast, etc
            - Use uma linguagem fluída não precisa especificar que segundo o documento a resposta é A ou B nem que a dúvida estava no campo descrição e que a justificativa ou o comentário contém determinada informação, assuma as informações como sendo suas
            - Em português brasileiro
            """

            response = st.session_state.model.generate_content(prompt)
            resposta = response.text

            # Adicionar resposta ao histórico
            st.session_state.messages.append({"role": "especialist", "content": resposta})
            
            # Mostrar resposta
            st.markdown(
                f'<div class="assistant-response">'
                f'<strong style="color: #4e89e8;">John Wiki:</strong> '
                f'<span style="color: #FFFFFF;">{resposta}</span>'
                f'</div>', 
                unsafe_allow_html=True
            )

        except Exception as e:
            error_msg = "Desculpe, estou com dificuldades técnicas no momento. Tente novamente em alguns instantes."
            st.session_state.messages.append({"role": "assistant", "content": error_msg})
            st.markdown(
                f'<div class="assistant-response">'
                f'<strong style="color: #4e89e8;">John Wiki:</strong> '
                f'<span style="color: #FFFFFF;">{error_msg}</span>'
                f'</div>', 
                unsafe_allow_html=True
            )

# Footer
st.markdown("""
<div class="footer">
💡 Dica: Faça perguntas específicas para respostas mais precisas
</div>
""", unsafe_allow_html=True)
