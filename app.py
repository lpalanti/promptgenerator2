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
    st.set_page_config(layout="wide")
    st.title("🔮 Gerador de Prompts Inteligente")

    # CSS personalizado
    st.markdown("""
        <style>
        .streamlit-expanderHeader {
            font-size: 14px;
        }
        div[data-testid="stVerticalBlock"] > div:first-child {
            position: fixed;
            width: 25%;
        }
        </style>
    """, unsafe_allow_html=True)

    # Carregar dados
    try:
        df = load_data()
    except Exception as e:
        st.error(f"Erro ao carregar arquivo: {str(e)}")
        return

    # Verificar estrutura do CSV
    if not all(col in df.columns for col in COLUNAS):
        st.error(f"CSV deve ter colunas: {', '.join(COLUNAS)}")
        return

    # Gerenciamento de estado
    if 'prompts_selecionados' not in st.session_state:
        st.session_state.prompts_selecionados = []

    # Barra lateral esquerda fixa para o prompt final
    with st.sidebar:
        st.header("📝 Prompt Final Montado")
        
        # Gera e edita o prompt
        prompt_automatico = "\n".join(st.session_state.prompts_selecionados)
        prompt_editavel = st.text_area(
            "Edite seu prompt:",
            value=prompt_automatico,
            height=300,
            key="prompt_editor"
        )
        
        # Botões de ação
        col1, col2 = st.columns(2)
        with col1:
            if st.button("📋 Copiar", use_container_width=True):
                st.session_state.prompt_copiado = prompt_editavel
                st.toast("Prompt copiado!", icon="✅")
        with col2:
            if st.button("🧹 Limpar", use_container_width=True, type="secondary"):
                st.session_state.prompts_selecionados = []
        
        st.markdown("---")
        
        # Formulário para novos prompts
        with st.expander("➕ Adicionar Novo Prompt", expanded=False):
            with st.form("new_prompt"):
                new_category = st.text_input("Nova Categoria")
                new_prompt = st.text_area("Texto do Prompt")
                
                if st.form_submit_button("Salvar no Banco", use_container_width=True):
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
                        st.success("✅ Prompt salvo!")
                    else:
                        st.warning("⚠ Preencha todos os campos!")

    # Área principal de seleção de prompts
    query_params = st.query_params
    selected_prompt = query_params.get("select", None)
    
    colunas = st.columns(3)
    categorias = df['category'].unique()

    for idx, category in enumerate(categorias):
        with colunas[idx % 3]:
            with st.expander(f"**{category}**", expanded=False):
                prompts = df[df['category'] == category]['prompt']
                
                for i, prompt in enumerate(prompts):
                    prompt_id = f"{category}_{i}"
                    btn_col, text_col = st.columns([0.2, 0.8])
                    
                    with text_col:
                        st.markdown(f"`{prompt}`")
                    
                    with btn_col:
                        if st.button("➕", key=f"btn_{prompt_id}", help="Adicionar ao prompt"):
                            if prompt not in st.session_state.prompts_selecionados:
                                st.session_state.prompts_selecionados.append(prompt)

                    # Seleção via URL
                    if selected_prompt == prompt_id:
                        if prompt not in st.session_state.prompts_selecionados:
                            st.session_state.prompts_selecionados.append(prompt)
                            st.experimental_set_query_params()

if __name__ == "__main__":
    main()
