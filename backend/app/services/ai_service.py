import asyncio
from fastapi import HTTPException
import ollama

class AIService:
    def __init__(self):
        self.model = "deepseek-r1:7b"
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
        content_base =  """#### 定位
                        - 智能助手名称：政务智能助手
                        - 主要任务：分析文档内容，提供准确的回答

                        #### 回答要求
                        1. 仔细阅读所有提供的文档内容
                        2. 保持回答简洁明了
                        3. 在回答末尾标注使用的文档来源
                        """
        response = ollama.chat(
            model=self.model,
            messages=[
                {"role": "system", "content": content_base},
                {"role": "user", "content": prompt}
            ]
        )
        return response['message']['content']


# 测试
if __name__ == "__main__":
    ai_service = AIService()
    # 运行异步函数
    asyncio.run(ai_service.get_response("我是王秘书，需要整理一份报告！"))

    
    