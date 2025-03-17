from fastapi import APIRouter, UploadFile, File, HTTPException, Query
from typing import List, Optional
from app.core.services import file_service, ai_service  # 从core.services导入

router = APIRouter()

@router.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    if file.filename.split('.')[-1].lower() not in ['pdf', 'doc', 'docx']:
        raise HTTPException(status_code=400, detail="不支持的文件格式")
    
    try:
        file_path = await file_service.save_file(file)
        return {"message": "文件上传成功", "file_path": file_path}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/search")
async def search_documents(query: str):
    try:
        # 搜索文档
        search_results = file_service.search(query)
        
        # 使用AI生成回答
        if search_results:
            # 按相关度排序并只使用前3个最相关的文档
            sorted_results = sorted(search_results, key=lambda x: x["score"], reverse=True)[:3]
            
            # 构建上下文，包含相关度信息
            context = []
            for idx, r in enumerate(sorted_results, 1):
                context.append(
                    f"文档{idx}（相关度：{r['score']:.2f}）：\n"
                    f"文件名：{r['filename']}\n"
                    f"内容：{r['content']}\n"
                )
            
            # 组合提示词
            prompt = (
                f"请基于以下按相关度排序的文档内容回答问题：{query}\n\n"
                f"参考文档：\n{''.join(context)}\n"
                f"请优先参考相关度更高的文档进行回答。"
            )
            
            ai_response = await ai_service.get_response(prompt)
            
            return {
                "ai_response": ai_response,
                "search_results": sorted_results  # 返回排序后的结果
            }
        
        return {
            "ai_response": None,
            "search_results": []
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/files")
async def list_files(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100)
):
    try:
        return file_service.get_file_list(page, page_size)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/rebuild-index")
async def rebuild_index():
    try:
        file_service.rebuild_index()
        return {"message": "索引重建成功"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))