import streamlit as st
import pandas as pd

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

    # Sidebar para adicionar novos e visualizar prompt final
    with st.sidebar:
        st.header("📝 Prompt Final Montado")
        if st.session_state.prompts_selecionados:
            prompt_final = "\n".join(st.session_state.prompts_selecionados)
            st.code(prompt_final)

            if st.button("Copiar Prompt", key="copiar_prompt"):
                st.session_state.prompt_copiado = prompt_final
                st.toast("Prompt copiado para área de transferência!", icon="✅")
        else:
            st.info("Selecione prompts para montar seu prompt final")

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
                    col1, col2 = st.columns([0.8, 0.2])
                    with col1:
                        st.markdown(f"`{prompt}`")
                    with col2:
                        if st.button("Selecionar", key=f"btn_{category}_{i}"):
                            if prompt not in st.session_state.prompts_selecionados:
                                st.session_state.prompts_selecionados.append(prompt)

if __name__ == "__main__":
    main()
