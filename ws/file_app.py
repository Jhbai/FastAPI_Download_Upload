from fastapi import FastAPI, File, UploadFile, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel, Field
from LLM.model import AI_Agent
from pytubefix import YouTube
import requests
import asyncio
import os

class Message(BaseModel):
    msg: str = Field(..., description="需要被回應的訊息")

class Youtube(BaseModel):
    url: str = Field(..., description="要下載的youtube影片")

async def download(url):
    try:
        yt = YouTube(url)
        path = "./youtube/"
        file = path + "video.mp4"
        for stream in yt.streams:
            if stream.resolution == "720p":
                print("找到影片url: {}".format(stream.url))
                response = requests.get(stream.url, stream=True)
                
                with open(file, "wb") as f:
                    print("開始下載...")
                    for chunk in response.iter_content(chunk_size=4096):
                        if chunk:  # 濾除空的 chunk
                            f.write(chunk)
                print("下載完成")
                break
    except Exception as e:
        print(f"下載失敗: {e}")

# 定義路由
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

# 初始化參數
UPLOAD_DIRECTORY = "./uploads"
os.makedirs(UPLOAD_DIRECTORY, exist_ok=True)

# API設計
# (1) 上傳檔案 API
@app.post("/upload/", tags = ["File_Operation"])
async def upload_file(file: UploadFile = File(...)):
    file_path = os.path.join(UPLOAD_DIRECTORY, file.filename)
    with open(file_path, "wb") as f:
        f.write(await file.read())
    return JSONResponse(content = {"data": file.filename, "msg": "File uploaded successfully", "error": ""})

# (2) 下載檔案 API
@app.get("/download/{filename}", tags = ["File_Operation"])
async def download_file(filename: str):
    file_path = os.path.join(UPLOAD_DIRECTORY, filename)
    if not os.path.exists(file_path):
        return {"error": "File not found"}
    return FileResponse(file_path, filename=filename)

# (3) 檔案清單 API
@app.get("/filelist/", tags = ["File_Operation"])
async def show_filelist():
    return JSONResponse(content = os.listdir("./uploads"))

# (4) 健康檢查 API
@app.get("/home", tags = ["System"])
async def home():
    return JSONResponse(content = {"status": "OK", "msg": "Welcome to the 熊熊 API"})

# (5) youtube下載
@app.post("/youtube_download", tags = ["youtube Service"])
async def AI(youtube: Youtube, background_tasks: BackgroundTasks):
    try:
        # 啟動背景下載任務
        asyncio.create_task(download(youtube.url))
        return FileResponse("./youtube/video.mp4", filename="video.mp4")
    except Exception as e:
        raise HTTPException(status_code=500, detail="下載失敗，請檢查伺服器日誌。")
 