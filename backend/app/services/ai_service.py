import asyncio
from fastapi import HTTPException
import ollama

class AIService:
    def __init__(self):
        self.model = "deepseek-r1:1.5b"
        self.timeout = 55  # 设置55秒超时
    
    async def get_response(self, prompt: str, context: list = None) -> str:
        try:
            # 使用 asyncio.wait_for 添加超时控制
            response = await asyncio.wait_for(
                self._get_ollama_response(prompt, context),
                timeout=self.timeout
            )
            print(response)
            return response
        except asyncio.TimeoutError:
            raise HTTPException(status_code=504, detail="AI模型响应超时，请稍后重试")
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"AI服务出现错误: {str(e)}")
    
    async def _get_ollama_response(self, prompt: str, context: list = None) -> str:
        content_beauty = "你是一个专业的美业顾问，请用专业且友善的语气回答，并且所有回答用中文。"
        content_base = "#### 定位\n- 智能助手名称 ：政务智能助手\n- 主要任务 ：对输入的内容进行分析，并用严谨且友善的语气，给出相应的回答。\n\n#### 能力\n- 文本分析 ：能够准确分析文档内容。\n\n#### 知识储备\n- 政务知识 ：\n  - 政治\n  - 经济\n  - 科技\n  - 城市治理\n  - 数据分析\n  - 教育\n  - 健康\n  - 国际\n  - 国内\n  - 社会\n\n#### 使用说明\n- 输入 ：相关政务文本。\n- 输出 ：只用言简意赅总结内容，不需要额外解释。回答的内容全部用中文输出。"
        response = ollama.chat(
            model=self.model,
            messages=[
                {"role": "system", "content": content_base},
                *[{"role": "user" if i % 2 == 0 else "assistant", "content": msg} 
                  for i, msg in enumerate(context or [])],
                {"role": "user", "content": prompt}
            ]
        )
        return response['message']['content']


# 测试
if __name__ == "__main__":
    ai_service = AIService()
    # 运行异步函数
    asyncio.run(ai_service.get_response("我是王秘书，需要整理一份报告！"))

    
    