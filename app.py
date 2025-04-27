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

# Função para adicionar prompt à seleção
def add_prompt(prompt):
    if prompt not in st.session_state.prompts_selecionados:
        st.session_state.prompts_selecionados.append(prompt)

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
        .prompt-btn {
            width: 100%;
            margin: 2px 0;
            text-align: left;
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

    # Inicializar session state
    if 'prompts_selecionados' not in st.session_state:
        st.session_state.prompts_selecionados = []

    # Barra lateral esquerda fixa
    with st.sidebar:
        st.header("📝 Prompt Final Montado")
        
        # Editor de prompt
        prompt_final = "\n".join(st.session_state.prompts_selecionados)
        edited_prompt = st.text_area(
            "Edite seu prompt:",
            value=prompt_final,
            height=300,
            key="prompt_editor"
        )
        
        # Botões de ação
        col1, col2 = st.columns(2)
        with col1:
            if st.button("📋 Copiar", use_container_width=True):
                st.session_state.prompt_copiado = edited_prompt
                st.toast("Prompt copiado!", icon="✅")
        with col2:
            if st.button("🧹 Limpar", use_container_width=True, type="secondary"):
                st.session_state.prompts_selecionados = []
                st.rerun()
        
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

    # Área principal de seleção
    categorias = df['category'].unique()
    colunas = st.columns(3)

    for idx, category in enumerate(categorias):
        with colunas[idx % 3]:
            with st.expander(f"**{category}**", expanded=False):
                prompts = df[df['category'] == category]['prompt']
                
                for prompt in prompts:
                    # Botão para seleção com estilo personalizado
                    if st.button(
                        prompt,
                        key=f"btn_{category}_{prompt}",
                        help="Clique para adicionar ao prompt",
                        on_click=add_prompt,
                        args=(prompt,),
                        use_container_width=True
                    ):
                        pass  # A ação é tratada pelo on_click

if __name__ == "__main__":
    main()
