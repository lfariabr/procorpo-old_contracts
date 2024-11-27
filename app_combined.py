import streamlit as st
from fastapi import HTTPException
import pandas as pd
from datetime import datetime
from dateutil import parser
import json
from supabase import create_client, Client

# Initialize Streamlit page config
st.set_page_config(
    page_title="Pró-Corpo Estética - Contratos Antigos",
    page_icon="💎",
    layout="wide"
)

# Custom CSS
st.markdown("""
    <style>
        .stApp {
            background-color: #FFF5F7;
        }
        .css-1d391kg {
            background-color: #FCE7F3;
        }
        .stButton>button {
            background-color: #D53F8C;
            color: white;
            border-radius: 20px;
            border: none;
            padding: 10px 25px;
        }
        .stButton>button:hover {
            background-color: #B83280;
        }
        h1, h2, h3 {
            color: #702459;
        }
    </style>
""", unsafe_allow_html=True)

# Initialize Supabase client
supabase = create_client(st.secrets["supabase_url"], st.secrets["supabase_key"])

def search_client(search_term: str, password: str):
    # Verify password
    if password != st.secrets["demo_password"]:
        raise HTTPException(status_code=401, detail="Invalid password")
    
    try:
        # First try exact match on CPF
        response = supabase.table("clients").select("*").filter(
            "cpf", "eq", search_term
        ).execute()
        
        if not response.data:
            # If no results found by CPF, try searching by name
            response = supabase.table("clients").select("*").filter(
                "name", "ilike", f"%{search_term}%"
            ).execute()
        
        return response.data if response.data else []
        
    except Exception as e:
        st.error(f"Error searching client: {str(e)}")
        return []

def format_date(date_str):
    if pd.isna(date_str):
        return ""
    try:
        date_obj = parser.parse(str(date_str))
        return date_obj.strftime("%d/%m/%Y")
    except:
        return str(date_str)

# Sidebar
st.sidebar.title("💎 Pró-Corpo")
st.sidebar.markdown("---")
st.sidebar.markdown("Sistema de Consulta de Contratos Antigos")

# Main content
st.title("🔍 Busca de Contratos")

# Search interface
with st.form("search_form"):
    col1, col2 = st.columns([3, 1])
    
    with col1:
        search_term = st.text_input("Nome ou CPF do cliente:", placeholder="Digite aqui...")
    
    with col2:
        password = st.text_input("Senha:", type="password")
    
    submitted = st.form_submit_button("Buscar 🔍")
    
    if submitted:
        if not search_term or not password:
            st.warning("⚠️ Por favor, preencha todos os campos!")
        else:
            with st.spinner("Buscando... 💫"):
                results = search_client(search_term, password)
                
                if results:
                    # Create a DataFrame with all results
                    df_rows = []
                    for result in results:
                        row = {
                            "CPF": result["cpf"],
                            "Name": result["name"],
                            "Status": result["status"],
                        }
                        try:
                            contract_details = result["contract_details"]
                            if isinstance(contract_details, str):
                                contract_details = json.loads(contract_details)
                            
                            # Format numeric values
                            ano_venda = contract_details.get("ano_venda", "")
                            if ano_venda and isinstance(ano_venda, (int, float)):
                                ano_venda = int(ano_venda)
                                
                            quantidade = contract_details.get("quantidade", "")
                            if quantidade and isinstance(quantidade, (int, float)):
                                quantidade = int(quantidade)
                                
                            valor_liquido = contract_details.get("valor_liquido", "")
                            if valor_liquido and isinstance(valor_liquido, (int, float)):
                                valor_liquido = f"R$ {valor_liquido:.2f}"
                                
                            valor_tabela = contract_details.get("valor_tabela_item", "")
                            if valor_tabela and isinstance(valor_tabela, (int, float)):
                                valor_tabela = f"R$ {valor_tabela:.2f}"
                                
                            valor_liquido_item = contract_details.get("valor_liquido_item", "")
                            if valor_liquido_item and isinstance(valor_liquido_item, (int, float)):
                                valor_liquido_item = f"R$ {valor_liquido_item:.2f}"
                                
                            valor_desconto = contract_details.get("valor_desconto_item", "")
                            if valor_desconto and isinstance(valor_desconto, (int, float)):
                                valor_desconto = f"R$ {valor_desconto:.2f}"
                                
                            desconto_percentual = contract_details.get("desconto_item_percentual", "")
                            if desconto_percentual and isinstance(desconto_percentual, (int, float)):
                                desconto_percentual = f"{desconto_percentual:.0f}%"
                            
                            # Add contract details as separate columns
                            row.update({
                                "Unidade": contract_details.get("unidade", ""),
                                "Ano Venda": ano_venda,
                                "Mês Venda": contract_details.get("mes_venda", ""),
                                "Procedimento/Produto": contract_details.get("procedimento_produto", ""),
                                "Quantidade": quantidade,
                                "Valor Líquido": valor_liquido,
                                "Valor Tabela": valor_tabela,
                                "Valor Líquido Item": valor_liquido_item,
                                "Valor Desconto": valor_desconto,
                                "Desconto": desconto_percentual,
                                "Data Venda": contract_details.get("data_venda", ""),
                            })
                        except Exception as e:
                            st.warning(f"Erro ao processar detalhes do contrato: {str(e)}")
                            row.update({
                                "ID": "", "Unidade": "", "Telefone": "", 
                                "Ano Venda": "", "Mês Venda": "", "Data Venda": "",
                                "Quantidade": "", "Valor Líquido": "", "Valor Tabela": "",
                                "Valor Líquido Item": "", "Valor Desconto": "",
                                "Procedimento/Produto": "", "Desconto": ""
                            })
                        
                        df_rows.append(row)
                    
                    df = pd.DataFrame(df_rows)
                    
                    # Display the results
                    st.markdown("### ✨ Informações Encontradas")
                    st.markdown(f"*{len(results)} resultados encontrados*")
                    st.dataframe(df.style.set_properties(**{
                        'background-color': '#FFF5F7',
                        'color': '#702459'
                    }), use_container_width=True)
                else:
                    st.warning("❌ Nenhum resultado encontrado ou erro na busca.")

st.sidebar.markdown("---")
st.sidebar.markdown("###### Pró-Corpo Lab 💜")
