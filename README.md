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

## Deployment

### FastAPI Backend

The FastAPI backend requires the following environment variables in a `.env` file:

```env
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_key
DEMO_PASSWORD=your_demo_password
```

### Streamlit Frontend

When deploying to Streamlit Cloud, you need to configure the following secrets in the Streamlit Cloud dashboard:

```toml
[secrets]
api_url = "YOUR_PRODUCTION_API_URL"  # URL where your FastAPI backend is deployed
supabase_url = "your_supabase_url"
supabase_key = "your_supabase_key"
demo_password = "your_demo_password"
```

## Streamlit Cloud Deployment

To deploy this application on Streamlit Cloud:

1. Create a new repository on GitHub and push this code to it
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Connect your GitHub account
4. Deploy the app by selecting your repository

### Required Secrets

In Streamlit Cloud, you need to set up the following secrets in the app settings:

```toml
[secrets]
api_url = "YOUR_API_URL"  # Your FastAPI backend URL
```

### Local Development

To run the app locally:

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Create a `.streamlit/secrets.toml` file with the required secrets
3. Run the app:
```bash
streamlit run streamlit_app.py
```
