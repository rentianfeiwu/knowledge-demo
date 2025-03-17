from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
import requests
import json
import base64
import os
import time
from dotenv import load_dotenv

load_dotenv()

router = APIRouter()

# 百度语音识别API配置
API_KEY = os.getenv("BAIDU_API_KEY")
SECRET_KEY = os.getenv("BAIDU_SECRET_KEY")

# 检查API密钥是否配置
if not API_KEY or not SECRET_KEY:
    print("警告: 百度语音识别API密钥未配置，请在.env文件中设置BAIDU_API_KEY和BAIDU_SECRET_KEY")

# 缓存access_token
token_cache = {
    "access_token": None,
    "expires_at": 0
}

# 获取百度语音识别的access_token
def get_access_token():
    # 检查缓存的token是否有效
    current_time = time.time()
    if token_cache["access_token"] and token_cache["expires_at"] > current_time:
        return token_cache["access_token"]
    
    # 获取新token
    url = f"https://aip.baidubce.com/oauth/2.0/token?grant_type=client_credentials&client_id={API_KEY}&client_secret={SECRET_KEY}"
    response = requests.post(url)
    result = response.json()
    
    if "access_token" in result:
        # 缓存token，有效期设为30天（实际有效期通常为30天）
        token_cache["access_token"] = result["access_token"]
        token_cache["expires_at"] = current_time + result.get("expires_in", 2592000) - 60  # 提前60秒过期
        return result["access_token"]
    else:
        raise HTTPException(status_code=500, detail="获取百度语音识别token失败")

@router.post("/speech-to-text")
async def speech_to_text(audio: UploadFile = File(...)):
    try:
        # 检查API密钥是否配置
        if not API_KEY or not SECRET_KEY:
            return JSONResponse(
                status_code=500,
                content={"message": "百度语音识别API密钥未配置"}
            )
            
        # 读取上传的音频文件
        audio_content = await audio.read()
        
        # 获取access_token
        access_token = get_access_token()
        
        # 根据文件类型确定format参数和采样率
        audio_format = "wav"  # 默认格式
        sample_rate = 16000   # 默认采样率
        
        if audio.filename:
            ext = audio.filename.split('.')[-1].lower()
            if ext in ["wav", "pcm"]:
                audio_format = ext
                sample_rate = 16000
            elif ext == "amr":
                audio_format = ext
                sample_rate = 8000
            elif ext == "m4a":
                audio_format = ext
                sample_rate = 16000  # m4a通常使用这个采样率
        
        # 调用百度语音识别API
        url = f"https://vop.baidu.com/server_api"
        
        headers = {
            "Content-Type": "application/json"
        }
        
        data = {
            "format": audio_format,
            "rate": sample_rate,
            "channel": 1,
            "cuid": "Uw1fVTzxWIMlKnXECvjuOgW27r4hOhLt",
            "token": access_token,
            "speech": base64.b64encode(audio_content).decode('utf-8'),
            "len": len(audio_content)
        }
        
        # 添加调试日志
        print(f"发送语音识别请求: 格式={audio_format}, 采样率={sample_rate}, 文件大小={len(audio_content)}")
        
        response = requests.post(url, headers=headers, data=json.dumps(data))
        result = response.json()
        
        # 添加响应日志
        print(f"语音识别响应: {result}")
        
        if result.get("err_no") == 0 and result.get("result"):
            return {"text": result["result"][0]}
        else:
            return JSONResponse(
                status_code=400,
                content={"message": "语音识别失败", "error": result.get("err_msg", "未知错误")}
            )
    except Exception as e:
        print(f"语音识别异常: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={"message": "服务器错误", "error": str(e)}
        )