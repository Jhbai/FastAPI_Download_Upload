from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
import os

app = FastAPI(
    title="熊熊API",
    description="提供電腦內網互通API",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 允許所有來源（或限制為特定來源）
    allow_credentials=True,
    allow_methods=["*"],  # 允許所有 HTTP 方法
    allow_headers=["*"],  # 允許所有 HTTP 標頭
)

UPLOAD_DIRECTORY = "./uploads"
os.makedirs(UPLOAD_DIRECTORY, exist_ok=True)

# 上傳檔案 API
@app.post("/upload/", tags = ["File_Operation"])
async def upload_file(file: UploadFile = File(...)):
    file_path = os.path.join(UPLOAD_DIRECTORY, file.filename)
    with open(file_path, "wb") as f:
        f.write(await file.read())
    return JSONResponse(content = {"data": file.filename, "msg": "File uploaded successfully", "error": ""})

# 下載檔案 API
@app.get("/download/{filename}", tags = ["File_Operation"])
async def download_file(filename: str):
    file_path = os.path.join(UPLOAD_DIRECTORY, filename)
    if not os.path.exists(file_path):
        return {"error": "File not found"}
    return FileResponse(file_path, filename=filename)

@app.get("/filelist/", tags = ["File_Operation"])
async def show_filelist():
    return JSONResponse(content = os.listdir("./uploads"))

# 健康檢查
@app.get("/home", tags = ["System"])
async def home():
    return JSONResponse(content = {"status": "OK", "msg": "Welcome to the 熊熊 API"})
