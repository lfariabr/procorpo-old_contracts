# Pró-Corpo Estética - Old Contracts Search Application

A FastAPI and Streamlit application for searching old client contracts from Pró-Corpo Estética's previous system. The application uses Supabase as the backend database and features a feminine-styled UI designed specifically for the brand.

## Features

- 💜 Search contracts by client name or CPF
- 💎 Beautiful, feminine-styled UI matching Pró-Corpo's brand
- 📊 Display contract details including values, discounts, and procedures
- 🔐 Secure access with password protection

## Setup

1. Create a virtual environment and activate it:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: .\venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up your environment variables:
   - Copy `.env.example` to `.env`
   - Fill in your Supabase credentials and demo password in `.env`:
     ```
     SUPABASE_URL=your_supabase_url
     SUPABASE_KEY=your_supabase_key
     DEMO_PASSWORD=your_password
     ```

## Running the Application

1. Start the FastAPI backend:
```bash
uvicorn app.api.main:app --reload --host 0.0.0.0 --port 8090
```

2. In a new terminal, start the Streamlit frontend:
```bash
cd app/frontend
streamlit run streamlit_app.py
```

## Importing Data

To import old contracts data:

1. Prepare your Excel file with the required columns
2. Rename your file to `contracts.xlsx` or modify the file path in `test_upload.py`
3. Run the import script:
```bash
python test_upload.py
```

## Database Schema

The Supabase database uses a "clients" table with:
- cpf (text)
- name (text)
- status (text)
- contract_details (jsonb)
- created_at (timestamp with time zone)
- updated_at (timestamp with time zone)
