from fastapi import HTTPException
from faster_whisper import WhisperModel
import os
from typing import Optional

class WhisperService:
    def __init__(self):
        # 加载模型，可以根据需要选择不同的模型大小
        self.model_size = "small"  # 可以是 tiny, base, small, medium, large
        self.model = WhisperModel(self.model_size, device="cpu", compute_type="int8")
        
    async def speech_to_text(self, audio_path: str, language: Optional[str] = None) -> str:
        try:
            # 使用fast-whisper进行语音识别
            segments, info = self.model.transcribe(
                audio_path,
                language=language,
                beam_size=5
            )
            
            # 将识别结果拼接成完整文本
            text = " ".join(segment.text for segment in segments)
            return text
            
        except Exception as e:
            raise HTTPException(
                status_code=500, 
                detail=f"语音识别失败: {str(e)}"
            )

# 单例模式
whisper_service = WhisperService()