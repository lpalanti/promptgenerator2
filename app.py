import streamlit as st
import pandas as pd
from urllib.parse import urlencode

# Configuração inicial
CSV_FILE = "prompts_database_complete.csv"
COLUNAS = ['category', 'prompt']

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
        return f"Prompt: {prompt}\nNegative Prompt: (deixe vazio se quiser)"
    elif modelo == "ComfyUI":
        return f"[Positive] {prompt} [Negative] low quality, blurry, distorted"
    elif modelo == "Automatic1111":
        return f"{prompt} ### Negative prompt: blurry, bad anatomy, worst quality"
    else:
        return prompt  # Caso escolha padrão

# Interface principal
def main():
    st.set_page_config(layout="wide")
    st.title("🔮 Gerador de Prompts Inteligente")

    # CSS para reduzir o tamanho dos títulos dos expansores
    st.markdown("""
        <style>
        .streamlit-expanderHeader {
            font-size: 14px;
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

    # Sessão para armazenar seleções
    if 'prompts_selecionados' not in st.session_state:
        st.session_state.prompts_selecionados = []

    # Captura seleção via URL
    query_params = st.query_params
    selected_prompt = query_params.get("select", None)

    # Sidebar para adicionar novos e visualizar prompt final
    with st.sidebar:
        st.header("📝 Prompt Final Montado")

        prompt_automatico = "\n".join(st.session_state.prompts_selecionados)

        if 'prompt_editavel' not in st.session_state:
            st.session_state.prompt_editavel = prompt_automatico

        if prompt_automatico != st.session_state.prompt_editavel:
            st.session_state.prompt_editavel = prompt_automatico

        st.session_state.prompt_editavel = st.text_area(
            "Prompt Final Montado",
            value=st.session_state.prompt_editavel,
            height=200
        )

        # Seletor de modelo de IA para adaptar o prompt
        modelo_selecionado = st.selectbox(
            "Selecionar Adaptador de Prompt",
            ("Padrão", "Midjourney", "Fooocus", "Leonardo AI", "ComfyUI", "Automatic1111")
        )

        prompt_adaptado = adaptar_prompt(st.session_state.prompt_editavel, modelo_selecionado)

        st.text_area(
            f"Prompt Adaptado para {modelo_selecionado}",
            value=prompt_adaptado,
            height=200,
            key="prompt_adaptado",
            disabled=True
        )

        if st.button("Copiar Prompt Adaptado"):
            st.session_state.prompt_copiado = prompt_adaptado
            st.toast(f"Prompt adaptado copiado!", icon="✅")

        if st.button("Limpar Seleção", key="limpar_selecao"):
            st.session_state.prompts_selecionados = []
            st.session_state.prompt_editavel = ""

        st.markdown("---")
        st.header("➕ Adicionar Novo Prompt")
        with st.form("new_prompt"):
            new_category = st.text_input("Nova Categoria")
            new_prompt = st.text_area("Novo Prompt")

            if st.form_submit_button("Adicionar ao Banco"):
                if new_category and new_prompt:
                    novo_prompt_df = pd.DataFrame([{
                        'category': new_category,
                        'prompt': new_prompt
                    }])

                    novo_prompt_df.to_csv(
                        CSV_FILE,
                        mode='a',
                        header=False,
                        sep=';',
                        index=False
                    )
                    st.success("Item adicionado!")
                else:
                    st.warning("Preencha ambos os campos!")

    # Construir interface de seleção em 3 colunas
    categorias = df['category'].unique()
    colunas = st.columns(3)

    for idx, category in enumerate(categorias):
        with colunas[idx % 3]:
            with st.expander(f"{category}"):
                prompts = df[df['category'] == category]['prompt']

                for i, prompt in enumerate(prompts):
                    prompt_id = f"{category}_{i}"

                    params = urlencode({"select": prompt_id})
                    link = f"?{params}"
                    st.markdown(f"[`{prompt}`]({link})")

                    if selected_prompt == prompt_id:
                        if prompt not in st.session_state.prompts_selecionados:
                            st.session_state.prompts_selecionados.append(prompt)
                            st.query_params.clear()

if __name__ == "__main__":
    main()
