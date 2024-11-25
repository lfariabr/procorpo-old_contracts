import streamlit as st
import requests
import pandas as pd
from datetime import datetime
from dateutil import parser
import json

# Configure the page
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

# API endpoint
API_URL = "http://localhost:8090"

def search_client(search_term: str, password: str):
    try:
        response = requests.post(
            f"{API_URL}/search_client",
            json={"search_term": search_term, "password": password}
        )
        
        if response.status_code == 200:
            return response.json()
        elif response.status_code == 401:
            st.error("Invalid password!")
        elif response.status_code == 404:
            st.warning("Client not found!")
        else:
            st.error(f"Error: {response.json()['detail']}")
        return None
    except Exception as e:
        st.error(f"Error connecting to the server: {str(e)}")
        return None

def import_excel(file, password: str):
    try:
        files = {"file": file}
        headers = {"accept": "application/json"}
        params = {"password": password}
        response = requests.post(
            f"{API_URL}/import_excel",
            files=files,
            params=params,
            headers=headers
        )
        
        if response.status_code == 200:
            result = response.json()
            if result["success"]:
                st.success(f"Successfully imported {result['rows_imported']} rows!")
                if result["errors"]:
                    st.warning("Some rows had errors:")
                    for error in result["errors"]:
                        st.write(f"- {error}")
            return result
        else:
            st.error(f"Error: {response.json()['detail']}")
            return None
    except Exception as e:
        st.error(f"Error connecting to the server: {str(e)}")
        return None

def get_all_clients(password: str):
    try:
        response = requests.get(
            f"{API_URL}/all_clients",
            params={"password": password}
        )
        
        if response.status_code == 200:
            return response.json()
        elif response.status_code == 401:
            st.error("Invalid password!")
        else:
            st.error(f"Error: {response.json()['detail']}")
        return None
    except Exception as e:
        st.error(f"Error connecting to the server: {str(e)}")
        return None

# Sidebar for navigation
st.sidebar.title("💎 Pró-Corpo Estética")
page = "Search Clients"  # Fixed to search only

# Password input in sidebar
st.sidebar.markdown("---")
password = st.sidebar.text_input("Senha de Acesso 🔐", type="password")
st.sidebar.markdown("---")
st.sidebar.markdown("💜 Sistema de Consulta")
st.sidebar.markdown("Contratos Antigos")

# Main content
st.title("💎 Pró-Corpo Estética")
st.subheader("Sistema de Consulta - Contratos Antigos 💜")
st.markdown("---")

st.markdown("### Buscar Contratos")
st.write("Digite o CPF ou Nome da cliente para buscar seus contratos anteriores")

search_term = st.text_input("CPF ou Nome da Cliente 👤")

if st.button("Buscar 🔍"):
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
                    # Parse contract details if it's a string
                    try:
                        contract_details = result["contract_details"]
                        if isinstance(contract_details, str):
                            contract_details = json.loads(contract_details)
                        
                        # Add contract details as separate columns
                        row.update({
                            "Unidade": contract_details.get("unidade", ""),
                            "Telefone": contract_details.get("telefone", ""),
                            "ID": contract_details.get("id", ""),
                            "Ano Venda": contract_details.get("ano_venda", ""),
                            "Mês Venda": contract_details.get("mes_venda", ""),
                            "Procedimento/Produto": contract_details.get("procedimento_produto", ""),
                            "Quantidade": contract_details.get("quantidade", ""),
                            "Valor Líquido": contract_details.get("valor_liquido", ""),
                            "Valor Tabela": contract_details.get("valor_tabela_item", ""),
                            "Valor Líquido Item": contract_details.get("valor_liquido_item", ""),
                            "Valor Desconto": contract_details.get("valor_desconto_item", ""),          
                            "Desconto (%)": contract_details.get("desconto_item_percentual", ""),
                            "Data Venda": contract_details.get("data_venda", ""),
                        })
                    except Exception as e:
                        st.warning(f"Error parsing contract details: {str(e)}")
                        # Add empty values for contract details columns
                        row.update({
                            "ID": "", "Unidade": "", "Telefone": "", 
                            "Ano Venda": "", "Mês Venda": "", "Data Venda": "",
                            "Quantidade": "", "Valor Líquido": "", "Valor Tabela": "",
                            "Valor Líquido Item": "", "Valor Desconto": "",
                            "Procedimento/Produto": "", "Desconto (%)": ""
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
