# -*- coding: utf-8 -*-
# 文件编码声明，指定使用 UTF-8 编码，支持中文字符

from fastapi import FastAPI, HTTPException, Request
# FastAPI   —— 主框架类，用于创建 Web 应用实例
# HTTPException —— 用于抛出 HTTP 错误响应（如 400、404）
# Request   —— 表示传入的 HTTP 请求对象，可读取请求体

from fastapi.responses import StreamingResponse
# StreamingResponse —— 用于返回流式响应（SSE / 逐 token 输出）

import json
# 标准库，用于序列化/反序列化 JSON 数据

import uuid
# 标准库，用于生成全局唯一标识符（UUID），区分不同会话和请求
import os, sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from integrated_qa_system.new_main import NewIntegratedQASystem
# 从 new_main.py 导入核心问答系统类（封装了 RAG + MySQL + Redis 逻辑）


# ── 应用初始化 ────────────────────────────────────────────────────────────────

app = FastAPI(
    title="集成问答系统 API",            # API 文档页面显示的标题
    description="基于 RAG + MySQL + Redis 的问答系统 FastAPI 接口"  # API 文档描述
)

qa_system = NewIntegratedQASystem()
# # 全局实例化问答系统，整个应用生命周期内共享同一个对象（避免重复加载模型）
#
# # ── 路由：主查询接口 ───────────────────────────────────────────────────────────
#
@app.post("/query")
# # 注册 POST /query 路由，客户端发送问题到此端点
async def handle_query(request: Request):
    # 异步处理函数，接收完整的 HTTP 请求对象

    try:
        body = await request.json()
        # 异步读取请求体并解析为 Python 字典；await 等待 I/O 完成
    except Exception:
        raise HTTPException(status_code=400, detail="无效的 JSON 数据")
        # 若请求体不是合法 JSON，返回 400 错误，终止后续处理

    query = body.get("query", "").strip() #body["query"]
    # 从请求体中取出查询字符串，默认空串，strip() 去除首尾空白

    source_filter = body.get("source_filter", None)
    # 可选参数：学科/来源过滤器，未传时为 None（不过滤）

    session_id = body.get("session_id", None)
    # 可选参数：会话 ID，用于多轮对话上下文管理；未传时后续自动生成

    if not query:
        raise HTTPException(status_code=400, detail="查询内容不能为空")
        # 查询为空字符串时拒绝请求，返回 400 错误

    if not session_id:
        session_id = str(uuid.uuid4())
        # 客户端未提供 session_id 时，服务端自动生成一个 UUID 作为会话标识

    valid_sources = qa_system.config.VALID_SOURCES
    # 从系统配置中读取合法的学科分类列表（如 ["AI", "JAVA", ...]）

    if source_filter and source_filter not in valid_sources:
        raise HTTPException(
            status_code=400,
            detail=f"无效的学科类别。支持: {valid_sources}"
            # source_filter 不在白名单内时，返回 400 并告知合法值
        )

    request_id = str(uuid.uuid4())
    # 为本次请求生成唯一 ID，用于后续"停止生成"时精确定位该请求


    # ── 内部生成器：逐 token 流式输出 ─────────────────────────────────────────

    def generate_response():
        # 同步生成器函数，每次 yield 一条 SSE 格式的数据帧

        try:
            for token, is_complete in qa_system.query(
                    query=query,                # 用户问题
                    source_filter=source_filter,# 学科过滤（可为 None）
                    session_id=session_id,      # 会话 ID，用于多轮上下文
            ):
                # 迭代问答系统返回的 (token文本, 是否完成) 元组


                message = {
                    "token": token,             # 当前生成的文本片段
                    "is_complete": is_complete, # False = 中间片段，True = 最后一帧
                    "session_id": session_id,
                    "request_id": request_id,
                }
                yield f"data: {json.dumps(message, ensure_ascii=False)}\n\n"
                # 将消息序列化为 JSON 并按 SSE 格式推送给客户端

                if is_complete:
                    break
                    # 问答系统自然结束时退出迭代（正常完成）

        except Exception as e:
            error_msg = f"处理查询时发生错误: {str(e)}"
            # 将异常转为可读字符串，便于日志记录和客户端展示

            qa_system.logger.error(error_msg)
            # 通过系统内置 logger 记录错误日志（写入文件或控制台）

            message = {
                "error": error_msg,             # 错误描述字段
                "is_complete": True,            # 发生错误时也标记流结束
                "session_id": session_id,
                "request_id": request_id,
            }
            yield f"data: {json.dumps(message, ensure_ascii=False)}\n\n"
            # 将错误信息推送给客户端，让前端感知异常



    return StreamingResponse(
        generate_response(),                    # 传入生成器，按需逐帧输出
        media_type="text/event-stream"          # 设置响应类型为 SSE（Server-Sent Events）
    )
#
# # ── 程序入口 ──────────────────────────────────────────────────────────────────
#
if __name__ == '__main__':
    import uvicorn
    # 仅在直接运行此文件时导入（避免不必要的依赖加载）

    uvicorn.run(app, host="0.0.0.0", port=8000)
    # host="0.0.0.0" 监听所有网卡，允许外部访问
    # port=8000      服务端口；生产环境建议通过配置文件或环境变量管理