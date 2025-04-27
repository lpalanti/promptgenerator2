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
    st.title("🔮 Gerador de Prompts Inteligente")
    
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

    # Sidebar para adicionar novos
    with st.sidebar:
        with st.form("new_prompt"):
            new_category = st.text_input("New Category")
            new_prompt = st.text_area("New Prompt")
            
            if st.form_submit_button("Adicionar ao Banco"):
                if new_category and novo_prompt:
                    new_prompt = pd.DataFrame([{
                        'category': nova_categoria,
                        'prompt': new_prompt
                    }])
                    
                    new_prompt.to_csv(
                        CSV_FILE,
                        mode='a',
                        header=False,
                        sep=';',
                        index=False
                    )
                    st.success("Item adicionado!")
                else:
                    st.warning("Preencha ambos os campos!")

    # Construir interface de seleção
    for category in df['category'].unique():
        with st.expander(f"**{category}**"):
            prompts = df[df['category'] == category]['prompt']
            
            for prompt in prompts:
                col1, col2 = st.columns([0.8, 0.2])
                with col1:
                    st.markdown(f"`{prompt}`")
                with col2:
                    if st.button("Selecionar", key=f"btn_{prompt}"):
                        if prompt not in st.session_state.prompts_selecionados:
                            st.session_state.prompts_selecionados.append(prompt)

    # Mostrar prompts selecionados
    st.markdown("---")
    st.subheader("📝 Prompt Final Montado")
    
    if st.session_state.prompts_selecionados:
        prompt_final = "\n".join(st.session_state.prompts_selecionados)
        st.code(prompt_final)
        
        if st.button("Copiar Prompt"):
            st.session_state.prompt_copiado = prompt_final
            st.toast("Prompt copiado para área de transferência!", icon="✅")
    else:
        st.info("Selecione prompts acima para montar seu prompt final")

    # Botão de limpar
    if st.button("Limpar Seleção"):
        st.session_state.prompts_selecionados = []

if __name__ == "__main__":
    main()
