import streamlit as st 
import pandas as pd
import requests
import traceback
from datetime import datetime
from dotenv import load_dotenv
import os

# Configurações iniciais
load_dotenv()  # Carrega variáveis do .env
CSV_FILE = "prompts_database_complete.csv"
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")  # Chave no .env
DEEPSEEK_API_URL = "https://api.deepseek.com/v1/chat/completions"

# Debug Mode
DEBUG = True  # Altere para False em produção

# ========== Funções Principais ==========
def load_data():
    """Carrega dados do CSV com tratamento de erros"""
    try:
        df = pd.read_csv(CSV_FILE, sep=';', encoding='utf-8', on_bad_lines='warn')
        if DEBUG: st.sidebar.success("CSV carregado com sucesso!")
        return df
    except Exception as e:
        st.error(f"Erro crítico ao carregar CSV: {str(e)}")
        st.stop()

def log_error(error_msg):
    """Registra erros em arquivo de log"""
    with open("app_errors.log", "a") as f:
        f.write(f"{datetime.now()} - {error_msg}\n")
    if DEBUG:
        st.sidebar.error(f"DEBUG: {error_msg}")

# ========== Interface ==========
def main():
    st.set_page_config(
        page_title="AI Prompt Generator Pro",
        page_icon="✨",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # CSS Personalizado
    st.markdown("""
        <style>
        /* Cores principais */
        :root {
            --primary: #4A90E2;
            --secondary: #F5F7FA;
        }
        
        /* Cabeçalho */
        .stApp header { background-color: var(--primary) !important; }
        
        /* Botões */
        .stButton>button {
            background-color: var(--primary) !important;
            color: white !important;
            border-radius: 8px;
            transition: all 0.3s;
        }
        .stButton>button:hover {
            opacity: 0.8;
            transform: scale(0.98);
        }
        
        /* Sidebar */
        [data-testid="stSidebar"] {
            background: var(--secondary) !important;
            border-right: 1px solid #e0e0e0;
        }
        
        /* Cards de Prompts */
        .prompt-card {
            padding: 1rem;
            margin: 0.5rem 0;
            border-radius: 10px;
            border: 1px solid #e0e0e0;
            transition: all 0.2s;
        }
        .prompt-card:hover {
            border-color: var(--primary);
            box-shadow: 0 3px 10px rgba(0,0,0,0.1);
        }
        </style>
    """, unsafe_allow_html=True)

    # Estado da sessão
    if 'prompts_selecionados' not in st.session_state:
        st.session_state.prompts_selecionados = []
    if 'negative_prompt' not in st.session_state:
        st.session_state.negative_prompt = ""

    # ========== Sidebar ==========
    with st.sidebar:
        st.title("⚙️ Controle")
        
        # Debug Info
        if DEBUG:
            st.subheader("🔍 Debug Mode")
            st.json({
                "selected_prompts": st.session_state.prompts_selecionados,
                "negative_prompt": st.session_state.negative_prompt
            })
        
        # Configurações
        modelo_selecionado = st.selectbox(
            "Modelo de IA:",
            ("Midjourney", "Fooocus", "Leonardo AI", "ComfyUI", "Automatic1111"),
            index=0
        )
        
        # Otimização
        if st.button("✨ Otimizar com DeepSeek", help="Gera prompt melhorado e negativo"):
            if st.session_state.prompts_selecionados:
                try:
                    prompt_base = "\n".join(st.session_state.prompts_selecionados)
                    improved, negative = melhorar_prompt(prompt_base, modelo_selecionado)
                    st.session_state.prompts_selecionados = [improved]
                    st.session_state.negative_prompt = negative
                    st.success("Otimização concluída!")
                except Exception as e:
                    log_error(f"Erro na otimização: {str(e)}")
                    st.error("Falha na otimização. Verifique logs.")
            else:
                st.warning("Adicione prompts antes de otimizar!")
        
        # Prompt Final
        st.divider()
        st.subheader("📝 Prompt Final")
        prompt_final = st.text_area(
            "Edite seu prompt:",
            value="\n".join(st.session_state.prompts_selecionados),
            height=200,
            key="prompt_editavel"
        )
        
        # Prompt Negativo
        st.subheader("🚫 Prompt Negativo")
        st.text_area(
            "Conteúdo a evitar:",
            value=st.session_state.negative_prompt,
            height=100,
            key="negative_prompt_area",
            disabled=False
        )

    # ========== Área Principal ==========
    st.title("🔮 AI Prompt Generator Pro")
    
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
                            key=f"btn_{categoria}_{promprompt}",
                            help=f"Adicionar '{prompt[:20]}...'",
                            use_container_width=True
                        ):
                            if prompt not in st.session_state.prompts_selecionados:
                                st.session_state.prompts_selecionados.append(prompt)
                                st.rerun()
    except Exception as e:
        log_error(f"Erro na interface principal: {str(e)}")
        st.error("Erro crítico na aplicação. Consulte os logs.")

# ========== Execução ==========
if __name__ == "__main__":
    main()
