import re
from parser import VideoSource, parse_video_id, parse_video_share_url

import uvicorn
from fastapi import FastAPI, Request, HTTPException, Query
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
import urllib.parse
import mimetypes
import requests

origins = ['*']

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

templates = Jinja2Templates(directory="templates")


@app.get("/", response_class=HTMLResponse)
async def read_item(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "title": "github.com/wujunwei928/parse-video-py Demo",
        },
    )


@app.get("/video/share/url/parse")
async def share_url_parse(url: str):
    url_reg = re.compile(r"http[s]?:\/\/[\w.-]+[\w\/-]*[\w.-]*\??[\w=&:\-\+\%]*[/]*")
    video_share_url = url_reg.search(url).group()

    try:
        video_info = await parse_video_share_url(video_share_url)
        return {"code": 200, "msg": "解析成功", "data": video_info.__dict__}
    except Exception as err:
        return {
            "code": 500,
            "msg": str(err),
        }


@app.get("/video/id/parse")
async def video_id_parse(source: VideoSource, video_id: str):
    try:
        video_info = await parse_video_id(source, video_id)
        return {"code": 200, "msg": "解析成功", "data": video_info.__dict__}
    except Exception as err:
        return {
            "code": 500,
            "msg": str(err),
        }


@app.get("/video/download")
async def download_video(url: str = Query(..., description="The URL of the video to download"),filename: str = Query("video.mp4", description="The filename for the downloaded video")):
    if not url:
        raise HTTPException(status_code=400, detail="No URL provided")

    try:
        # 发起HTTP GET请求
        response = requests.get(url, stream=True)
        response.raise_for_status()  # 检查请求是否成功

        # 获取视频的MIME类型
        content_type = response.headers.get('content-type')

        # 根据MIME类型确定文件扩展名
        extension = mimetypes.guess_extension(content_type) or '.mp4'
        full_filename = f"{filename}{extension}"
        # 使用 urllib.parse.quote 对文件名进行编码
        encoded_filename = urllib.parse.quote(full_filename)
        # 创建StreamingResponse对象
        return StreamingResponse(
            response.iter_content(chunk_size=1024),
            media_type=content_type,
            headers={
                "Content-Disposition": f"attachment; filename*=UTF-8''{encoded_filename}"
            }
        )
    
    except requests.RequestException as e:
        # 请求失败时处理异常
        raise HTTPException(status_code=500, detail=str(e))
    
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)