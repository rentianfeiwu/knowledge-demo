from fastapi import APIRouter, UploadFile, File, HTTPException
from app.services.whisper_service import whisper_service
import os
import tempfile

router = APIRouter()

@router.post("/speech-to-text")
async def speech_to_text(audio: UploadFile = File(...)):
    try:
        # 创建临时文件
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp_file:
            # 保存上传的音频文件
            content = await audio.read()
            tmp_file.write(content)
            tmp_file_path = tmp_file.name
            
        # 调用whisper服务进行语音识别
        text = await whisper_service.speech_to_text(tmp_file_path)
        
        # 删除临时文件
        os.unlink(tmp_file_path)
        
        return {"text": text}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))