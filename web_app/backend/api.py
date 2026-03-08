from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
import os
import shutil
import uuid
from key_manager import KeyManager
from encryptor import Encryptor
from file_handler import FileHandler

app = FastAPI(title="Secure Encryption API")

# Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Temp directories for processing
TEMP_DIR = "temp_processing"
KEYS_DIR = "keys"
os.makedirs(TEMP_DIR, exist_ok=True)
os.makedirs(KEYS_DIR, exist_ok=True)

km = KeyManager(key_directory=KEYS_DIR)

@app.post("/generate-key")
async def generate_key(name: str = Form(...)):
    if not name:
        raise HTTPException(status_code=400, detail="Key name is required")
    
    if not name.endswith(".key"):
        name += ".key"
        
    key = km.generate_key()
    path = km.save_key(key, filename=name)
    
    return FileResponse(path, filename=name, media_type='application/octet-stream')

@app.post("/encrypt-text")
async def encrypt_text(text: str = Form(...), key_file: UploadFile = File(...)):
    key_data = await key_file.read()
    try:
        enc = Encryptor(key_data)
        ciphertext = enc.encrypt_text(text)
        return {"ciphertext": ciphertext}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/decrypt-text")
async def decrypt_text(ciphertext: str = Form(...), key_file: UploadFile = File(...)):
    key_data = await key_file.read()
    try:
        enc = Encryptor(key_data)
        plaintext = enc.decrypt_text(ciphertext)
        return {"plaintext": plaintext}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/encrypt-file")
async def encrypt_file(file: UploadFile = File(...), key_file: UploadFile = File(...)):
    job_id = str(uuid.uuid4())
    job_dir = os.path.join(TEMP_DIR, job_id)
    os.makedirs(job_dir, exist_ok=True)
    
    input_path = os.path.join(job_dir, file.filename)
    key_data = await key_file.read()
    
    with open(input_path, "wb") as f:
        shutil.copyfileobj(file.file, f)
        
    try:
        fh = FileHandler(key_data)
        output_path = fh.encrypt_file(input_path)
        return FileResponse(output_path, filename=os.path.basename(output_path))
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/decrypt-file")
async def decrypt_file(file: UploadFile = File(...), key_file: UploadFile = File(...)):
    job_id = str(uuid.uuid4())
    job_dir = os.path.join(TEMP_DIR, job_id)
    os.makedirs(job_dir, exist_ok=True)
    
    input_path = os.path.join(job_dir, file.filename)
    key_data = await key_file.read()
    
    with open(input_path, "wb") as f:
        shutil.copyfileobj(file.file, f)
        
    try:
        fh = FileHandler(key_data)
        output_path = fh.decrypt_file(input_path)
        return FileResponse(output_path, filename=os.path.basename(output_path))
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
