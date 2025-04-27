import streamlit as st 
import pandas as pd
import requests
import traceback
from datetime import datetime
from dotenv import load_dotenv
import os

# Configurações iniciais
load_dotenv()
CSV_FILE = "prompts_database_complete.csv"
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
DEEPSEEK_API_URL = "https://api.deepseek.com/v1/chat/completions"

# Modos de operação
DEBUG = True  # Altere para False em produção

# ========== FUNÇÕES PRINCIPAIS ==========
@st.cache_data
def load_data():
    """Carrega e armazena em cache os dados do CSV"""
    try:
        df = pd.read_csv(
            CSV_FILE,
            sep=';',
            encoding='utf-8',
            on_bad_lines='skip'
        )
        return df.dropna().reset_index(drop=True)
    except Exception as e:
        log_error(f"Falha ao carregar CSV: {str(e)}")
        st.error("Erro crítico no carregamento do banco de dados!")
        st.stop()

def log_error(error_msg):
    """Registra erros em arquivo de log"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open("app_errors.log", "a") as f:
        f.write(f"[{timestamp}] {error_msg}\n")
    if DEBUG:
        st.sidebar.error(f"DEBUG: {error_msg}")

def melhorar_prompt(prompt_base, ferramenta):
    """Otimiza o prompt usando DeepSeek API com tratamento específico"""
    headers = {
        "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
        "Content-Type": "application/json"
    }
    
    templates = {
        "Midjourney": {
            "system": "Especialista em Midjourney. Use --v 5 --style raw e outros parâmetros técnicos relevantes.",
            "negative": "Gere prompt negativo técnico para Midjourney"
        },
        "Fooocus": {
            "system": "Expert em Fooocus. Utilize tags <s> e parâmetros como --detailed --realistic",
            "negative": "Elementos indesejados para Fooocus"
        },
        "Leonardo AI": {
            "system": "Mestre em Leonardo AI. Formate com 'Prompt:' e 'Negative Prompt:' separados",
            "negative": "Conteúdo inadequado para plataformas seguras"
        },
        "ComfyUI": {
            "system": "Especialista em ComfyUI. Use [Positive]/[Negative]",
            "negative": "Problemas comuns em workflows"
        },
        "Automatic1111": {
            "system": "Expert em Automatic1111. Utilize '### Negative prompt:'",
            "negative": "Artefatos comuns no Stable Diffusion"
        }
    }

    try:
        # Otimização do prompt principal
        response = requests.post(
            DEEPSEEK_API_URL,
            headers=headers,
            json={
                "model": "deepseek-chat",
                "messages": [
                    {
                        "role": "system", 
                        "content": f"{templates[ferramenta]['system']} Otimize para: {ferramenta}"
                    },
                    {
                        "role": "user",
                        "content": f"OPTIMIZE PARA {ferramenta.upper()}:\n\n{prompt_base}"
                    }
                ],
                "temperature": 0.7
            },
            timeout=30
        )

        response.raise_for_status()
        improved_prompt = response.json()['choices'][0]['message']['content']

        # Geração do prompt negativo
        negative_response = requests.post(
            DEEPSEEK_API_URL,
            headers=headers,
            json={
                "model": "deepseek-chat",
                "messages": [
                    {
                        "role": "system",
                        "content": f"{templates[ferramenta]['negative']} para {ferramenta}"
                    },
                    {
                        "role": "user",
                        "content": improved_prompt
                    }
                ],
                "temperature": 0.5
            },
            timeout=30
        )

        negative_response.raise_for_status()
        negative_prompt = negative_response.json()['choices'][0]['message']['content']

        return improved_prompt, negative_prompt

    except requests.exceptions.RequestException as e:
        log_error(f"Erro na API: {str(e)}")
        return prompt_base, "Erro temporário. Tente novamente."
    except Exception as e:
        log_error(f"Erro geral: {str(e)}")
        return prompt_base, "Erro na otimização"

# ========== INTERFACE ==========
def main():
    st.set_page_config(
        page_title="Otimizador de Prompts AI",
        page_icon="🤖",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    # CSS Customizado
    st.markdown("""
        <style>
        :root {
            --primary: #2E86C1;
            --secondary: #28B463;
            --background: #FDFEFE;
        }

        .stApp {
            background-color: var(--background);
        }

        .stButton>button {
            background: var(--primary) !important;
            color: white !important;
            border-radius: 8px;
            transition: all 0.3s;
            padding: 0.5rem 1rem;
        }

        .stButton>button:hover {
            opacity: 0.9;
            transform: scale(0.98);
        }

        .prompt-card {
            padding: 1rem;
            margin: 0.5rem 0;
            background: white;
            border-radius: 10px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
            border: 1px solid #EAEDED;
        }

        [data-testid="stExpander"] {
            background: white !important;
            border-radius: 10px !important;
        }
        </style>
    """, unsafe_allow_html=True)

    # Estado da sessão
    if 'prompts' not in st.session_state:
        st.session_state.prompts = []
    if 'negative' not in st.session_state:
        st.session_state.negative = ""
    if 'historico' not in st.session_state:
        st.session_state.historico = []

    # Sidebar
    with st.sidebar:
        st.title("⚙️ Controle")
        
        ferramenta = st.selectbox(
            "Selecione a Ferramenta:",
            ("Midjourney", "Fooocus", "Leonardo AI", "ComfyUI", "Automatic1111"),
            index=0
        )

        if st.button("🚀 Otimizar Prompt", help="Clique para processar com IA"):
            if st.session_state.prompts:
                with st.spinner("Processando com DeepSeek..."):
                    try:
                        prompt_base = "\n".join(st.session_state.prompts)
                        melhorado, negativo = melhorar_prompt(prompt_base, ferramenta)
                        st.session_state.prompts = [melhorado]
                        st.session_state.negative = negativo
                        st.session_state.historico.insert(0, {
                            "prompt": melhorado,
                            "ferramenta": ferramenta,
                            "data": datetime.now().strftime("%d/%m %H:%M"),
                            "negativo": negativo
                        })
                        st.success("Otimização concluída!")
                    except Exception as e:
                        st.error("Erro durante o processamento")
            else:
                st.warning("Adicione prompts antes de otimizar!")

        st.divider()
        st.subheader("📝 Prompt Final")
        st.session_state.prompts = st.text_area(
            "Edite seu prompt:",
            value="\n".join(st.session_state.prompts),
            height=200,
            label_visibility="collapsed"
        ).split('\n')

        st.subheader("🚫 Prompt Negativo")
        st.text_area(
            "Elementos a evitar:",
            value=st.session_state.negative,
            height=100,
            label_visibility="collapsed"
        )

    # Área principal
    st.title("🎨 Gerador de Prompts Inteligente")
    
    try:
        df = load_data()
        categorias = df['category'].unique()
        
        cols = st.columns(3)
        for idx, prompt in enumerate(df[df['category'] == categoria]['prompt']):
            btn_key = f"btn_{categoria}_{idx}_{prompt[:20]}"  # Chave única com índice
            if st.button(
            prompt,
            key=btn_key,  # Chave única para cada botão
            help=f"Adicionar: {prompt[:50]}...",
            use_container_width=True
            ):
                if prompt not in st.session_state.prompts_selecionados:
                    st.session_state.prompts_selecionados.append(prompt)
                    st.rerun()

        # Histórico de versões
        st.divider()
        st.subheader("🕒 Histórico de Versões")
        for item in st.session_state.historico[:5]:
            with st.expander(f"{item['ferramenta']} - {item['data']}"):
                st.markdown(f"**Prompt Otimizado:**\n{item['prompt']}")
                st.markdown(f"**Negativo:**\n{item['negativo']}")

    except Exception as e:
        log_error(f"Erro na interface: {str(e)}")
        st.error("Erro na aplicação. Verifique os logs.")

if __name__ == "__main__":
    main()
