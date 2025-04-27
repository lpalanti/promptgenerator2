import streamlit as st
import pandas as pd
import csv

CSV_FILE = "prompts_database_complete.csv"

def load_data():
    try:
        # Especificar encoding e delimitador
        return pd.read_csv(
            CSV_FILE,
            delimiter=';',  # Garantir que está usando vírgula
            header=0,       # Usar primeira linha como cabeçalho
            encoding='utf-8',
            quotechar='"',
            quoting=csv.QUOTE_MINIMAL,
            on_bad_lines='warn'  # Mostrar linhas problemáticas
        )
    except Exception as e:
        st.error(f"Erro ao carregar CSV: {str(e)}")
        return pd.DataFrame(columns=['Category', 'Subcategory', 'Item', 'Translation'])

def main():
    st.title("🔮 Gerador de Prompts Inteligente")
    
    # Carregar dados
    df = load_data()
    
    # Sessão para armazenar o prompt
    if 'selected_items' not in st.session_state:
        st.session_state.selected_items = []
    
    # Sidebar para adicionar novos itens
    with st.sidebar:
        st.header("➕ Adicionar Novo Item")
        with st.form("new_item_form"):
            category = st.text_input("Categoria")
            subcategory = st.text_input("Subcategoria")
            english = st.text_input("Termo em Inglês")
            portuguese = st.text_input("Tradução em Português")
            
            if st.form_submit_button("Salvar"):
                if category and subcategory and english and portuguese:
                    new_row = pd.DataFrame([{
                        'Category': category,
                        'Subcategory': subcategory,
                        'Item': english,
                        'Translation': portuguese
                    }])
                    new_row.to_csv(CSV_FILE, mode='a', header=False, index=False)
                    st.success("Item adicionado com sucesso!")
                else:
                    st.error("Preencha todos os campos!")

    # Construir interface de seleção
    for category in df['Category'].unique():
        with st.expander(f"**{category}**"):
            cat_df = df[df['Category'] == category]
            for subcategory in cat_df['Subcategory'].unique():
                st.markdown(f"##### {subcategory}")
                sub_df = cat_df[cat_df['Subcategory'] == subcategory]
                cols = st.columns(3)
                
                for idx, row in sub_df.iterrows():
                    col = cols[idx % 3]
                    translation = row['Translation']
                    
                    # HTML/CSS para tooltip
                    col.markdown(f"""
                    <div style="position:relative;margin:5px 0;">
                        <button style="width:100%;padding:8px;margin:2px 0;cursor:pointer;"
                            onmouseover="this.nextElementSibling.style.display='block'"
                            onmouseout="this.nextElementSibling.style.display='none'"
                            onclick="this.classList.toggle('selected')">
                            {row['Item']}
                        </button>
                        <div style="display:none;position:absolute;background:#f0f2f6;padding:5px;border-radius:4px;z-index:1000;">
                            {translation}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    if col.button(f"Selecionar {row['Item']}"):
                        if row['Item'] not in st.session_state.selected_items:
                            st.session_state.selected_items.append(row['Item'])
    
    # Mostrar prompt construído
    st.markdown("---")
    st.subheader("📝 Prompt Final")
    st.code(" ".join(st.session_state.selected_items))
    
    if st.button("Limpar Seleção"):
        st.session_state.selected_items = []

if __name__ == "__main__":
    main()
