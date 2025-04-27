import streamlit as st 
import pandas as pd
import requests
from urllib.parse import urlencode

# Configuração inicial
CSV_FILE = "prompts_database_complete.csv"
COLUNAS = ['category', 'prompt']
DEEPSEEK_API_KEY = "sk-44c48f425dc44730a5180c832ba604b3"
DEEPSEEK_API_URL = "https://api.deepseek.com/v1/chat/completions"

# Carregar dados do CSV
def load_data():
    return pd.read_csv(
        CSV_FILE,
        sep=';',
        encoding='utf-8',
        on_bad_lines='warn'
    )

# Função para adaptar prompt para diferentes modelos
def adaptar_prompt(prompt, modelo):
    adaptacoes = {
        "Midjourney": lambda p: f"{p} --v 5 --q 2 --style raw",
        "Fooocus": lambda p: f"<s>{p}</s> --detailed --realistic",
        "Leonardo AI": lambda p: f"Prompt: {p}\nNegative Prompt: {st.session_state.negative_prompt}",
        "ComfyUI": lambda p: f"[Positive] {p} [Negative] {st.session_state.negative_prompt}",
        "Automatic1111": lambda p: f"{p} ### Negative prompt: {st.session_state.negative_prompt}"
    }
    return adaptacoes.get(modelo, lambda p: p)(prompt)

# Função para melhorar o prompt usando a API DeepSeek
def melhorar_prompt(prompt_base, modelo):
    headers = {
        "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
        "Content-Type": "application/json"
    }
    
    # Melhorar prompt positivo
    system_message = f"""Você é um especialista em melhorar prompts para {modelo}. 
    Melhore este prompt para seguir as especificações técnicas do modelo e ser mais descritivo, criativo e detalhado."""
    
    data = {
        "model": "deepseek-chat",
        "messages": [
            {"role": "system", "content": system_message},
            {"role": "user", "content": prompt_base}
        ],
        "temperature": 0.7
    }
    
    response = requests.post(DEEPSEEK_API_URL, headers=headers, json=data)
    
    if response.status_code == 200:
        improved_prompt = response.json()['choices'][0]['message']['content']
        
        # Gerar prompt negativo
        negative_data = {
            "model": "deepseek-chat",
            "messages": [
                {"role": "system", "content": "Gere um prompt negativo relevante para o prompt fornecido, considerando os principais elementos que devem ser evitados."},
                {"role": "user", "content": improved_prompt}
            ],
            "temperature": 0.5
        }
        
        negative_response = requests.post(DEEPSEEK_API_URL, headers=headers, json=negative_data)
        
        if negative_response.status_code == 200:
            return improved_prompt, negative_response.json()['choices'][0]['message']['content']
    
    return prompt_base, "low quality, blurry, distorted"  # Fallback

# Interface principal
def main():
    st.set_page_config(layout="wide")
    st.title("🔮 Gerador de Prompts Inteligente")

    # CSS customizado
    st.markdown("""
        <style>
        .prompt-box {
            padding: 0.5rem;
            margin: 0.2rem 0;
            border-radius: 5px;
            border: 1px solid #e1e4e8;
            cursor: pointer;
            transition: all 0.2s;
        }
        .prompt-box:hover {
            background-color: #f8f9fa;
            border-color: #0366d6;
        }
        .stButton>button {
            width: 100%;
            transition: all 0.2s;
        }
        .stTextArea textarea {
            min-height: 150px;
        }
        </style>
    """, unsafe_allow_html=True)

    # Carregar dados
    try:
        df = load_data()
    except Exception as e:
        st.error(f"Erro ao carregar arquivo: {str(e)}")
        return

    # Verificar estrutura
    if not all(col in df.columns for col in COLUNAS):
        st.error(f"CSV deve ter colunas: {', '.join(COLUNAS)}")
        return

    # Inicializar session state
    if 'prompts_selecionados' not in st.session_state:
        st.session_state.prompts_selecionados = []
    if 'negative_prompt' not in st.session_state:
        st.session_state.negative_prompt = ""

    # Sidebar
    with st.sidebar:
        st.header("📝 Prompt Final Montado")
        
        # Área de edição do prompt
        prompt_final = "\n".join(st.session_state.prompts_selecionados)
        st.session_state.prompt_editavel = st.text_area(
            "Editar Prompt Final:",
            value=prompt_final,
            height=200,
            key="final_prompt"
        )

        # Seleção de modelo
        modelo_selecionado = st.selectbox(
            "Modelo de IA:",
            ("Midjourney", "Fooocus", "Leonardo AI", "ComfyUI", "Automatic1111", "Outro")
        )

        # Botões de ação
        col1, col2 = st.columns(2)
        with col1:
            if st.button("✨ Melhorar Prompt", help="Otimizar usando DeepSeek"):
                with st.spinner("Otimizando..."):
                    improved, negative = melhorar_prompt(
                        st.session_state.prompt_editavel, 
                        modelo_selecionado
                    )
                    st.session_state.prompt_editavel = improved
                    st.session_state.negative_prompt = negative
                    st.toast("Prompt otimizado com sucesso!", icon="✅")
        
        with col2:
            if st.button("🔄 Limpar Tudo"):
                st.session_state.prompts_selecionados = []
                st.session_state.prompt_editavel = ""
                st.session_state.negative_prompt = ""
        
        # Prompt negativo
        st.text_area(
            "Prompt Negativo:",
            value=st.session_state.negative_prompt,
            height=100,
            key="negative_prompt_area"
        )

        # Prompt adaptado
        st.divider()
        st.header("⚙️ Prompt Adaptado")
        prompt_adaptado = adaptar_prompt(st.session_state.prompt_editavel, modelo_selecionado)
        st.code(prompt_adaptado, language="text")

    # Lista de prompts por categoria
    categorias = df['category'].unique()
    cols = st.columns(3)
    
    for idx, categoria in enumerate(categorias):
        with cols[idx % 3]:
            with st.expander(f"📁 {categoria.upper()}"):
                prompts = df[df['category'] == categoria]['prompt']
                for prompt in prompts:
                    if st.button(
                        prompt,
                        key=f"btn_{categoria}_{prompt}",
                        help="Clique para adicionar ao prompt",
                        use_container_width=True
                    ):
                        if prompt not in st.session_state.prompts_selecionados:
                            st.session_state.prompts_selecionados.append(prompt)
                            st.rerun()

if __name__ == "__main__":
    main()
