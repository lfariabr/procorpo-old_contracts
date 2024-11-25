import requests
import os

# URL of your FastAPI endpoint
url = "http://localhost:8090/import_excel"

# Path to the Excel file
file_path = "contracts.xlsx"  # Changed to the original file

# Password for authentication
params = {
    "password": "ProCorpoCttsAntigos"
}

# Check if file exists
if not os.path.exists(file_path):
    print(f"Error: File {file_path} not found!")
    exit(1)

print(f"Found file: {file_path}")
print(f"File size: {os.path.getsize(file_path)} bytes")

# Open and send the file
with open(file_path, "rb") as f:
    files = {
        "file": (os.path.basename(file_path), f, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    }
    
    print("Sending request...")
    response = requests.post(url, params=params, files=files)
    
    print(f"\nStatus Code: {response.status_code}")
    print("Response:")
    print(response.text)
