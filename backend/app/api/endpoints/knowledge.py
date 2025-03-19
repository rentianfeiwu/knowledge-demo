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
        search_results = file_service.search(query)
        
        if search_results:
            # 只取相关度最高的文档
            best_match = max(search_results, key=lambda x: x["score"])
            
            # 构建提示词
            prompt = (
                f"问题：{query}\n\n"
                f"参考文档（相关度：{best_match['score']:.2f}）：\n"
                f"标题：{best_match['filename']}\n"
                f"内容：{best_match['content']}\n\n"
                "请根据上述文档内容回答问题。回答要简明扼要，并在末尾标注文档来源。"
            )
            
            ai_response = await ai_service.get_response(prompt)
            
            return {
                "ai_response": ai_response,
                "search_results": [best_match]
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