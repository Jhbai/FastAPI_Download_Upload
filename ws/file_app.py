from fastapi import FastAPI, File, UploadFile, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from concurrent.futures import ThreadPoolExecutor
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
    yt = YouTube(url)
    path = "./youtube/"
    file = path + "video.mp4"
    stream = yt.streams.filter(res="720p").first()  # 選擇 720p 畫質
    if stream:
        print(f"找到影片 URL: {stream.url}")

        # 取得文件大小並設定分段
        file_size = stream.filesize
        num_chunks = 4  # 將文件分成 4 段
        chunk_size = file_size // num_chunks

        def download_chunk(start, end, index):
            headers = {"Range": f"bytes={start}-{end}"}
            response = requests.get(stream.url, headers=headers, stream=True)
            with open(f"{file}_part{index}", "wb") as f:
                for chunk in response.iter_content(chunk_size=1024*1024):  # 1 MB
                    if chunk:
                        f.write(chunk)
            print(f"完成第 {index+1} 段下載")

        # 創建多線程下載
        with ThreadPoolExecutor(max_workers=num_chunks) as executor:
            futures = []
            for i in range(num_chunks):
                start = i * chunk_size
                end = start + chunk_size - 1 if i < num_chunks - 1 else file_size - 1
                futures.append(executor.submit(download_chunk, start, end, i))

            for future in futures:
                future.result()  # 等待所有段完成

        # 合併文件
        with open(file, "wb") as f:
            for i in range(num_chunks):
                part_file = f"{file}_part{i}"
                with open(part_file, "rb") as pf:
                    f.write(pf.read())
                os.remove(part_file)  # 刪除臨時分段文件

        print("下載完成，已合併所有文件")
    else:
        print("找不到符合條件的影片串流")

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
 