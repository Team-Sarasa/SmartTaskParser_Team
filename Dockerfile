FROM python:3.11-slim

WORKDIR /app

# 依存関係コピー & インストール
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# アプリ本体をコピー
COPY . .

# Cloud Run のポートはデフォルト 8080
ENV PORT=8080

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]
