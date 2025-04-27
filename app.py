import streamlit as st
import pandas as pd
import requests

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
    if modelo == "Midjourney":
        return f"{prompt} --v 5 --q 2 --style raw"
    elif modelo == "Fooocus":
        return f"<s>{prompt}</s> --detailed --realistic"
    elif modelo == "Leonardo AI":
        return f"Prompt: {prompt}"
    elif modelo == "ComfyUI":
        return f"[Positive] {prompt}"
    elif modelo == "Automatic1111":
        return f"{prompt}"
    else:
        return prompt  # Padrão

# Função para melhorar prompt e gerar também o prompt negativo via DeepSeek
def melhorar_prompt(prompt_base, modelo):
    headers = {
        "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
        "Content-Type": "application/json"
    }
    prompt_inicial = f"""
Você é um especialista em criação de prompts para inteligência artificial.

Melhore o seguinte prompt, adaptando-o para a ferramenta {modelo}, deixando-o mais descritivo, criativo, e detalhado.
Além disso, crie também um **prompt negativo** separado.

Prompt base: {prompt_base}

Formato de resposta:
PROMPT POSITIVO: <seu texto aqui>
PROMPT NEGATIVO: <seu texto aqui>
"""
    data = {
        "model": "deepseek-chat",
        "messages": [{"role": "user", "content": prompt_inicial}],
        "temperature": 0.7
    }

    response = requests.post(DEEPSEEK_API_URL, headers=headers, json=data)

    if response.status_code == 200:
        resposta = response.json()
        content = resposta['choices'][0]['message']['content']

        # Extrair prompt positivo e negativo
        positivo = ""
        negativo = ""
        try:
            positivo = content.split("PROMPT POSITIVO:")[1].split("PROMPT NEGATIVO:")[0].strip()
            negativo = content.split("PROMPT NEGATIVO:")[1].strip()
        except Exception as e:
            positivo = content
            negativo = ""

        return positivo, negativo
    else:
        return f"Erro: {response.status_code}", ""

# Interface principal
def main():
    st.set_page_config(layout="wide")
    st.title("🔮 Gerador de Prompts Inteligente")

    # Estilizar com CSS
    st.markdown("""
        <style>
        .streamlit-expanderHeader {
            font-size: 16px;
            font-weight: bold;
        }
        .prompt-button {
            background-color: #f0f2f6;
            border: none;
            padding: 6px 10px;
            margin: 3px 0;
            width: 100%;
            text-align: left;
            border-radius: 8px;
            cursor: pointer;
        }
        .prompt-button:hover {
            background-color: #e0e4ec;
        }
        </style>
    """, unsafe_allow_html=True)

    # Carregar dados
    try:
        df = load_data()
    except Exception as e:
        st.error(f"Erro ao carregar arquivo: {str(e)}")
        return

    if not all(col in df.columns for col in COLUNAS):
        st.error(f"CSV deve ter colunas: {', '.join(COLUNAS)}")
        return

    # Sessão para armazenar estado
    if 'prompts_selecionados' not in st.session_state:
        st.session_state.prompts_selecionados = []
    if 'prompt_negativo' not in st.session_state:
        st.session_state.prompt_negativo = ""

    # Sidebar
    with st.sidebar:
        st.header("📝 Prompt Final")

        prompt_automatico = "\n".join(st.session_state.prompts_selecionados)
        st.session_state.prompt_editavel = st.text_area(
            "Prompt Positivo:",
            value=prompt_automatico,
            height=200
        )

        st.text_area(
            "Prompt Negativo (automático):",
            value=st.session_state.prompt_negativo,
            height=100,
            disabled=True
        )

        modelo_selecionado = st.selectbox(
            "Selecionar Adaptador de Prompt",
            ("Midjourney", "Fooocus", "Leonardo AI", "ComfyUI", "Automatic1111")
        )

        if st.button("Melhorar e Adaptar com DeepSeek"):
            with st.spinner("Otimizando com DeepSeek..."):
                positivo, negativo = melhorar_prompt(st.session_state.prompt_editavel, modelo_selecionado)
                st.session_state.prompt_editavel = adaptar_prompt(positivo, modelo_selecionado)
                st.session_state.prompt_negativo = negativo
                st.success("Prompt otimizado e adaptado!")

        if st.button("Limpar Tudo"):
            st.session_state.prompts_selecionados = []
            st.session_state.prompt_editavel = ""
            st.session_state.prompt_negativo = ""

        st.markdown("---")
        st.header("➕ Adicionar Novo Prompt")
        with st.form("add_prompt"):
            new_category = st.text_input("Categoria")
            new_prompt = st.text_area("Novo Prompt")

            if st.form_submit_button("Adicionar"):
                if new_category and new_prompt:
                    new_row = pd.DataFrame([{'category': new_category, 'prompt': new_prompt}])
                    new_row.to_csv(CSV_FILE, mode='a', header=False, sep=';', index=False)
                    st.success("Prompt adicionado!")
                else:
                    st.warning("Preencha todos os campos!")

    # Exibição dos prompts
    categorias = df['category'].unique()
    colunas = st.columns(3)

    for idx, categoria in enumerate(categorias):
        with colunas[idx % 3]:
            with st.expander(f"📂 {categoria}"):
                prompts = df[df['category'] == categoria]['prompt']

                for prompt in prompts:
                    if st.button(prompt, key=f"{categoria}_{prompt}"):
                        st.session_state.prompts_selecionados.append(prompt)

if __name__ == "__main__":
    main()
