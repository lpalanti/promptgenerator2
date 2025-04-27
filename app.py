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

# Interface principal
def main():
    st.set_page_config(layout="wide")  # Para usar melhor o espaço na tela
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
        # Gera o prompt final automaticamente
        prompt_automatico = "\n".join(st.session_state.prompts_selecionados)

    # Cria um campo de texto editável
    if 'prompt_editavel' not in st.session_state:
        st.session_state.prompt_editavel = prompt_automatico

    # Atualiza o campo com o prompt automático sempre que ele mudar
            if prompt_automatico != st.session_state.prompt_editavel:
            st.session_state.prompt_editavel = prompt_automatico

    # Campo editável
        st.session_state.prompt_editavel = st.text_area(
        "Prompt Final Montado",
        value=st.session_state.prompt_editavel,
        height=200
        )

    if st.button("Copiar Prompt", key="copiar_prompt"):
        st.session_state.prompt_copiado = st.session_state.prompt_editavel
        st.toast("Prompt copiado para área de transferência!", icon="✅")

        if st.button("Limpar Seleção", key="limpar_selecao"):
            st.session_state.prompts_selecionados = []

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
    colunas = st.columns(3)  # 3 colunas

    for idx, category in enumerate(categorias):
        with colunas[idx % 3]:  # Distribui as categorias entre as colunas
            with st.expander(f"{category}"):
                prompts = df[df['category'] == category]['prompt']

                for i, prompt in enumerate(prompts):
                    prompt_id = f"{category}_{i}"

                    # Cria link clicável para selecionar o prompt
                    params = urlencode({"select": prompt_id})
                    link = f"?{params}"
                    st.markdown(f"[`{prompt}`]({link})")

                    # Verifica se foi selecionado via URL
                    if selected_prompt == prompt_id:
                        if prompt not in st.session_state.prompts_selecionados:
                             st.session_state.prompts_selecionados.append(prompt)
                             # Limpa a URL para não ficar selecionando de novo
                             st.query_params.clear()# Verifica se foi selecionado via URL
                    if selected_prompt == prompt_id:
                        if prompt not in st.session_state.prompts_selecionados:
                            st.session_state.prompts_selecionados.append(prompt)
                            # Limpa a URL para não ficar selecionando de novo
                            st.experimental_set_query_params()

if __name__ == "__main__":
    main()
