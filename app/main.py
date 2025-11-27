from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from .schemas import ParseAndCreateRequest, Task
from . import task_service


app = FastAPI(
    title="SmartTaskParser API",
    version="0.1.0",
)


# 必要ならローカル開発用に CORS を緩めておく（あとで調整でOK）
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 本番では絞る
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health_check():
    """
    動作確認用ヘルスチェックエンドポイント。
    """
    return {"status": "ok"}


@app.post("/tasks/parse-and-create", response_model=Task)
def parse_and_create_task(req: ParseAndCreateRequest):
    """
    自然文テキストからタスクを生成し、Notion に登録するメイン API。

    入力:
        {
          "text": "明日の午前までに研究のスライド直す",
          "source": "line",        # 任意。省略時は "line"
          "user_id": "xxxx"        # 任意
        }

    出力:
        Task モデル(JSON)
    """
    try:
        task = task_service.create_task_from_text(
            text=req.text,
            source=req.source,
            user_id=req.user_id,
        )
        return task
    except Exception as e:
        # TODO: logging に置き換える（今はとりあえず print）
        print(f"[ERROR] /tasks/parse-and-create failed: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")


# ローカル実行用（`python -m app.main` で起動できるようにしておく）
if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
    )
