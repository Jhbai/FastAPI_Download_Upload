from fastapi import FastAPI, File, UploadFile
from fastapi.responses import FileResponse
import os

app = FastAPI(
    title="熊熊API",
    description="提供電腦內網互通API",
    version="1.0.0"
)

UPLOAD_DIRECTORY = "./uploads"
os.makedirs(UPLOAD_DIRECTORY, exist_ok=True)

# 上傳檔案 API
@app.post("/upload/", tags = ["File_Operation"])
async def upload_file(file: UploadFile = File(...)):
    file_path = os.path.join(UPLOAD_DIRECTORY, file.filename)
    with open(file_path, "wb") as f:
        f.write(await file.read())
    return {"filename": file.filename, "message": "File uploaded successfully"}

# 下載檔案 API
@app.get("/download/{filename}", tags = ["File_Operation"])
async def download_file(filename: str):
    file_path = os.path.join(UPLOAD_DIRECTORY, filename)
    if not os.path.exists(file_path):
        return {"error": "File not found"}
    return FileResponse(file_path, filename=filename)

# 健康檢查
@app.get("/home", tags = ["System"])
async def home():
    return {"status": "OK", "msg": "Welcome to the 熊熊 API"}
