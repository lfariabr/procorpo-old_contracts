from fastapi import FastAPI, HTTPException, Depends, status, UploadFile, File, Query
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
from typing import Optional, List
import os
from dotenv import load_dotenv
from supabase import create_client, Client
import pandas as pd
from io import BytesIO
from datetime import datetime

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI(title="Old Contracts API")

# Initialize Supabase client
supabase_url = os.getenv("SUPABASE_URL")
supabase_key = os.getenv("SUPABASE_KEY")
supabase = create_client(supabase_url, supabase_key)

# Initialize password from .env file
DEMO_PASSWORD = os.getenv("DEMO_PASSWORD")

class ClientSearch(BaseModel):
    search_term: str
    password: str

class ClientResponse(BaseModel):
    cpf: str
    name: str
    contract_details: dict
    status: str
    created_at: str
    updated_at: str

class ImportResponse(BaseModel):
    success: bool
    rows_imported: int
    errors: List[str]

@app.post("/search_client", response_model=List[ClientResponse])
async def search_client(client_search: ClientSearch):
    if client_search.password != DEMO_PASSWORD:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid password"
        )
    
    try:
        # Search by CPF (exact match) or name (case-insensitive contains)
        response = supabase.table("clients").select("*").filter(
            "cpf", "eq", client_search.search_term
        ).execute()
        
        if not response.data:
            # If no results found by CPF, try searching by name
            response = supabase.table("clients").select("*").filter(
                "name", "ilike", f"%{client_search.search_term}%"
            ).execute()
        
        if not response.data:
            return []
        
        # Return all matches
        return [
            ClientResponse(
                cpf=client["cpf"],
                name=client["name"],
                contract_details=client["contract_details"],
                status=client["status"],
                created_at=client["created_at"],
                updated_at=client["updated_at"]
            )
            for client in response.data
        ]
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@app.post("/import_excel", response_model=ImportResponse)
async def import_excel(file: UploadFile = File(...), password: str = Query(None)):
    if password != DEMO_PASSWORD:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid password"
        )
    
    try:
        print(f"Received file: {file.filename}")
        content = await file.read()
        print(f"File size: {len(content)} bytes")
        
        # Save to a temporary file first
        temp_file = "temp_upload.xlsx"
        
        try:
            # Save the original file
            with open(temp_file, "wb") as f:
                f.write(content)
            
            # Read Excel file with specific column names
            expected_columns = [
                'ID', 'Data Venda', 'Unidade', 'Cliente', 'Valor Líquido',
                'Procedimento / Produto', 'Quantidade', 'Valor Tabela Item',
                '% Desconto Item', 'Valor Desconto Item', 'Valor Líquido Item',
                'Mês Venda', 'Ano Venda', 'Telefone'
            ]
            
            print("Reading Excel file...")
            df = pd.read_excel(temp_file)
            
            # Verify and fix column names if needed
            current_columns = df.columns.tolist()
            print(f"Current columns: {current_columns}")
            
            # Replace NaN values with 0
            df = df.fillna(0)
            
            print("Successfully read file")
            print(f"Columns found: {df.columns.tolist()}")
            
            # Process each row
            success_count = 0
            row_errors = []
            
            for index, row in df.iterrows():
                try:
                    # Create data dictionary with all fields
                    data = {
                        'cpf': str(row.get('CPF', '')).strip() if pd.notna(row.get('CPF', '')) else '',
                        'name': str(row.get('Cliente', '')).strip() if pd.notna(row.get('Cliente', '')) else '',
                        'status': str(row.get('Status', '')).strip() if pd.notna(row.get('Status', '')) else '',
                        'contract_details': {
                            'id': str(row.get('ID', '')),
                            'data_venda': str(row.get('Data Venda', '')),
                            'unidade': str(row.get('Unidade', '')),
                            'cliente': str(row.get('Cliente', '')),
                            'valor_liquido': float(row.get('Valor Líquido', 0)),
                            'procedimento_produto': str(row.get('Procedimento / Produto', '')),
                            'quantidade': float(row.get('Quantidade', 0)),
                            'valor_tabela_item': float(row.get('Valor Tabela Item', 0)),
                            'desconto_item_percentual': float(row.get('% Desconto Item', 0)),
                            'valor_desconto_item': float(row.get('Valor Desconto Item', 0)),
                            'valor_liquido_item': float(row.get('Valor Líquido Item', 0)),
                            'mes_venda': str(row.get('Mês Venda', '')),
                            'ano_venda': str(row.get('Ano Venda', '')),
                            'telefone': str(row.get('Telefone', ''))
                        }
                    }
                    
                    # Insert into Supabase
                    supabase.table('clients').insert(data).execute()
                    success_count += 1
                    print(f"Successfully imported row {index + 2}")
                    
                except Exception as row_error:
                    error_msg = f"Error in row {index + 2}: {str(row_error)}"
                    print(error_msg)
                    row_errors.append(error_msg)
            
            return ImportResponse(
                success=True,
                rows_imported=success_count,
                errors=row_errors
            )
            
        except Exception as e:
            print(f"Error processing file: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Error processing file: {str(e)}"
            )
        finally:
            # Clean up temporary file
            if os.path.exists(temp_file):
                os.remove(temp_file)
            
    except Exception as e:
        if isinstance(e, HTTPException):
            raise
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@app.get("/all_clients")
async def get_all_clients(password: str):
    if password != DEMO_PASSWORD:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid password"
        )
    
    try:
        response = supabase.table("clients").select("*").execute()
        return response.data
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@app.get("/health")
async def health_check():
    return {"status": "healthy"}
