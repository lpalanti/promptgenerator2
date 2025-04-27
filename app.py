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
DEBUG = True  # Ativar/desativar modo debug

# ========== FUNÇÕES PRINCIPAIS ==========
def load_data():
    """Carrega dados do CSV com tratamento robusto de erros"""
    try:
        df = pd.read_csv(
            CSV_FILE,
            sep=';',
            encoding='utf-8',
            on_bad_lines='skip'
        )
        if DEBUG:
            st.sidebar.success("✅ CSV carregado com sucesso!")
            st.sidebar.write(f"📊 Total de prompts: {len(df)}")
        return df.dropna()
    except Exception as e:
        log_error(f"CRÍTICO: Erro ao carregar CSV - {str(e)}")
        st.error("🚨 Falha crítica no carregamento do banco de dados!")
        st.stop()

def log_error(error_msg):
    """Registra erros em arquivo com timestamp"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open("app_errors.log", "a") as f:
        f.write(f"[{timestamp}] {error_msg}\n")
    if DEBUG:
        st.sidebar.error(f"🐞 DEBUG: {error_msg}")

def melhorar_prompt(prompt_base, ferramenta):
    """Otimiza o prompt usando DeepSeek com tratamento específico por ferramenta"""
    headers = {
        "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
        "Content-Type": "application/json"
    }
    
    instrucoes = {
        "Midjourney": {
            "system": "Você é um expert em Midjourney. Otimize o prompt incluindo parâmetros técnicos como --v 5 --style raw",
            "negative": "Gere um prompt negativo técnico para Midjourney focando em evitar artefatos comuns"
        },
        "Fooocus": {
            "system": "Especialista em Fooocus. Use tags XML <s> e parâmetros como --detailed --realistic",
            "negative": "Elementos a evitar na sintaxe Fooocus"
        },
        "Leonardo AI": {
            "system": "Expert em Leonardo AI. Formate com campos 'Prompt:' e 'Negative Prompt:' separados",
            "negative": "Conteúdo inadequado para plataformas seguras"
        },
        "ComfyUI": {
            "system": "Mestre em ComfyUI. Use a estrutura [Positive] e [Negative]",
            "negative": "Problemas comuns em workflows do ComfyUI"
        },
        "Automatic1111": {
            "system": "Especialista em Automatic1111. Use '### Negative prompt:'",
            "negative": "Artifacts comuns no Stable Diffusion"
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
                        "content": f"{instrucoes[ferramenta]['system']}. Otimize para: {ferramenta}"
                    },
                    {
                        "role": "user",
                        "content": f"OPTIMIZE PARA {ferramenta.upper()}:\n\n{prompt_base}"
                    }
                ],
                "temperature": 0.7
            }
        )

        if response.status_code != 200:
            raise Exception(f"API Error: {response.status_code} - {response.text}")
            
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
                        "content": f"Gere prompt negativo para {ferramenta}. {instrucoes[ferramenta]['negative']}"
                    },
                    {
                        "role": "user",
                        "content": improved_prompt
                    }
                ],
                "temperature": 0.5
            }
        )

        negative_prompt = negative_response.json()['choices'][0]['message']['content'] if negative_response.status_code == 200 else "low quality, blurry"

        return improved_prompt, negative_prompt

    except Exception as e:
        log_error(f"Falha na API: {str(e)}")
        return prompt_base, "Erro na otimização. Tente novamente."

# ========== INTERFACE ==========
def main():
    st.set_page_config(
        page_title="AI Prompt Optimizer Pro",
        page_icon="🚀",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    # CSS Customizado
    st.markdown("""
        <style>
        :root {
            --primary: #2c3e50;
            --secondary: #3498db;
            --background: #ecf0f1;
        }

        .stApp {
            background-color: var(--background);
        }

        .stButton>button {
            background: var(--secondary) !important;
            color: white !important;
            border-radius: 8px;
            transition: transform 0.2s;
        }

        .stButton>button:hover {
            transform: scale(0.98);
            opacity: 0.9;
        }

        .prompt-card {
            padding: 1rem;
            margin: 0.5rem 0;
            background: white;
            border-radius: 10px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
            transition: all 0.3s;
        }

        .prompt-card:hover {
            box-shadow: 0 5px 15px rgba(0,0,0,0.2);
        }
        </style>
    """, unsafe_allow_html=True)

    # Estado da sessão
    session_defaults = {
        'prompts': [],
        'negative': "",
        'historico': []
    }
    for key, value in session_defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

    # Sidebar
    with st.sidebar:
        st.title("⚙️ Controle")
        
        # Seletor de ferramenta
        ferramenta = st.selectbox(
            "Ferramenta de IA:",
            ("Midjourney", "Fooocus", "Leonardo AI", "ComfyUI", "Automatic1111"),
            index=0
        )

        # Botão de otimização
        if st.button("✨ Otimizar Prompt", type="primary"):
            if st.session_state.prompts:
                try:
                    prompt_base = "\n".join(st.session_state.prompts)
                    melhorado, negativo = melhorar_prompt(prompt_base, ferramenta)
                    st.session_state.prompts = [melhorado]
                    st.session_state.negative = negativo
                    st.session_state.historico.append({
                        "prompt": melhorado,
                        "ferramenta": ferramenta,
                        "data": datetime.now().strftime("%d/%m/%Y %H:%M")
                    })
                    st.success("Otimização concluída!")
                except Exception as e:
                    log_error(str(e))
                    st.error("Falha na otimização. Verifique os logs.")
            else:
                st.warning("Adicione prompts antes de otimizar!")

        # Área de prompts
        st.divider()
        st.subheader("📝 Prompt Final")
        prompt_final = st.text_area(
            "Edite seu prompt:",
            value="\n".join(st.session_state.prompts),
            height=200,
            key="editable_prompt"
        )

        st.subheader("🚫 Prompt Negativo")
        st.text_area(
            "Elementos a evitar:",
            value=st.session_state.negative,
            height=100,
            key="negative_prompt_area"
        )

    # Área principal
    st.title("🎨 AI Prompt Optimizer Pro")
    
    try:
        df = load_data()
        categorias = df['category'].unique()
        cols = st.columns(3)
        
        for idx, categoria in enumerate(categorias):
            with cols[idx % 3]:
                with st.expander(f"📁 {categoria.upper()}", expanded=True):
                    for prompt in df[df['category'] == categoria]['prompt']:
                        if st.button(
                            prompt,
                            key=f"btn_{categoria}_{prompt[:10]}",
                            help=f"Adicionar: {prompt[:50]}...",
                            use_container_width=True
                        ):
                            if prompt not in st.session_state.prompts:
                                st.session_state.prompts.append(prompt)
                                st.rerun()

        # Seção de histórico
        st.divider()
        st.subheader("📜 Histórico de Otimizações")
        for item in st.session_state.historico:
            with st.expander(f"{item['ferramenta']} - {item['data']}"):
                st.code(item['prompt'], language="text")

    except Exception as e:
        log_error(f"Erro na interface: {str(e)}")
        st.error("Erro crítico na aplicação. Consulte os logs.")

if __name__ == "__main__":
    main()
