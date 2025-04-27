import streamlit as st
import json
from pathlib import Path

# Configuração inicial
DB_FILE = "prompt_database.json"
DEFAULT_DATA = {
    "categories": {
        "Tone": {
            "subcategories": {
                "Formal": ["Academic", "Professional"],
                "Informal": ["Casual", "Friendly"]
            }
        },
        "Structure": {
            "subcategories": {
                "Types": ["Essay", "Report", "List"]
            }
        }
    },
    "translations": {
        "Academic": "Acadêmico",
        "Professional": "Profissional",
        "Casual": "Casual",
        "Friendly": "Amigável",
        "Essay": "Ensaio",
        "Report": "Relatório",
        "List": "Lista"
    }
}

# Carregar ou criar o banco de dados
def load_database():
    if not Path(DB_FILE).exists():
        with open(DB_FILE, 'w') as f:
            json.dump(DEFAULT_DATA, f)
    with open(DB_FILE) as f:
        return json.load(f)

def save_database(data):
    with open(DB_FILE, 'w') as f:
        json.dump(data, f, indent=2)

# Interface principal
def main():
    st.title("🔮 Gerador de Prompts Inteligente")
    
    # Carregar dados
    db = load_database()
    
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
                    # Atualizar estrutura de dados
                    if category not in db['categories']:
                        db['categories'][category] = {"subcategories": {}}
                    if subcategory not in db['categories'][category]['subcategories']:
                        db['categories'][category]['subcategories'][subcategory] = []
                    if english not in db['categories'][category]['subcategories'][subcategory]:
                        db['categories'][category]['subcategories'][subcategory].append(english)
                    db['translations'][english] = portuguese
                    save_database(db)
                    st.success("Item adicionado com sucesso!")
                else:
                    st.error("Preencha todos os campos!")

    # Construir interface de seleção
    for category, cat_data in db['categories'].items():
        with st.expander(f"**{category}**"):
            for subcategory, items in cat_data['subcategories'].items():
                st.markdown(f"##### {subcategory}")
                cols = st.columns(3)
                
                for idx, item in enumerate(items):
                    col = cols[idx % 3]
                    translation = db['translations'].get(item, "Sem tradução")
                    
                    # HTML/CSS para tooltip
                    col.markdown(f"""
                    <div style="position:relative;margin:5px 0;">
                        <button style="width:100%;padding:8px;margin:2px 0;cursor:pointer;"
                            onmouseover="this.nextElementSibling.style.display='block'"
                            onmouseout="this.nextElementSibling.style.display='none'"
                            onclick="this.classList.toggle('selected')">
                            {item}
                        </button>
                        <div style="display:none;position:absolute;background:#f0f2f6;padding:5px;border-radius:4px;z-index:1000;">
                            {translation}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    if col.button(f"Selecionar {item}"):
                        if item not in st.session_state.selected_items:
                            st.session_state.selected_items.append(item)
    
    # Mostrar prompt construído
    st.markdown("---")
    st.subheader("📝 Prompt Final")
    st.code(" ".join(st.session_state.selected_items))
    
    if st.button("Limpar Seleção"):
        st.session_state.selected_items = []

if __name__ == "__main__":
    main()
