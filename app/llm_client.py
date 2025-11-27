import os
from datetime import datetime, date, timedelta
from typing import Dict, Any, Optional

from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()

GEMINI_API_KEY = os.getenv("LLM_API_KEY")
if not GEMINI_API_KEY:
    raise ValueError("Environment variable LLM_API_KEY is not set.")

genai.configure(api_key=GEMINI_API_KEY)


# ----------------------------
# メイン関数
# ----------------------------
def parse_task_text(text: str) -> Dict[str, Any]:
    """
    Gemini API を使って、日本語の自然文タスク文を Task JSON に変換する。

    Returns:
        dict: {
            "title": str,
            "due_date": str | None,
            "priority": str,
            "notes": str | None
        }
    """

    prompt = build_prompt(text)
    model = genai.GenerativeModel("gemini-2.5-flash")

    response = model.generate_content(prompt)

    # Gemini は時々余計なテキストを返すので JSON 抽出が必要
    json_dict = extract_json_from_response(response.text)

    # 最終的に日付形式の整形
    json_dict["due_date"] = normalize_date(json_dict.get("due_date"))

    return json_dict


# ----------------------------
# プロンプト構築
# ----------------------------
def build_prompt(text: str) -> str:
    """
    タスク抽出用の system prompt + user prompt を組み立てる
    """

    today = date.today().isoformat()

    return f"""
あなたは日本語の自然文からタスク情報を抽出するシステムです。

ユーザーが入力した文章を解析し、次の JSON を出力してください：

{{
  "title": string,              # タスク名
  "due_date": string | null,    # YYYY-MM-DD 形式 or null
  "priority": "low" | "medium" | "high",
  "notes": string | null
}}

# ルール
- 現在日付は {today}
- 「今日」「明日」「あさって」「金曜」「来週」など相対表現は日付に変換してください。
- 日付不明なら null にしてください。
- タスク名は短く簡潔にまとめてください。
- 文章の要点以外は notes に入れても構いません。
- 出力は必ず純粋な JSON のみ。

# 入力文
{text}

JSON のみを返してください。
"""


# ----------------------------
# Gemini の回答から JSON 抽出
# ----------------------------
def extract_json_from_response(text: str) -> Dict[str, Any]:
    """
    Gemini の回答から JSON 部分のみ抽出。
    JSON をパースして dict にする。
    """

    import json
    import re

    # { ... } を全部抜き出す（最初の JSON を使う）
    match = re.search(r"\{[\s\S]*\}", text)
    if not match:
        raise ValueError(f"Gemini response does not contain JSON: {text}")

    json_str = match.group(0)

    try:
        return json.loads(json_str)
    except json.JSONDecodeError:
        raise ValueError(f"Invalid JSON returned from Gemini: {json_str}")


# ----------------------------
# 日付の正規化
# ----------------------------
def normalize_date(value: Optional[str]) -> Optional[str]:
    """
    - "2025-01-20" など正規の ISO ならそのまま
    - "明日" "金曜" などを Gemini が返す場合 → 補正
    - null / 空 なら None
    """

    if not value:
        return None

    # ISO 形式チェック
    try:
        datetime.fromisoformat(value)
        return value
    except ValueError:
        pass

    # Gemini が相対語を残してしまった場合の保険
    return _parse_relative_date(value)


# ----------------------------
# 相対日付の解釈
# ----------------------------
def _parse_relative_date(s: str) -> Optional[str]:
    """
    Gemini の返した日付が「明日」などだった場合の救済処理。
    主要な相対表現だけカバーしておく。
    """

    s = s.strip()

    today = date.today()

    if s in ["今日", "本日"]:
        return today.isoformat()

    if s in ["明日", "あした"]:
        return (today + timedelta(days=1)).isoformat()

    if s in ["あさって"]:
        return (today + timedelta(days=2)).isoformat()

    # 平日名（例：金曜）
    weekdays = ["月", "火", "水", "木", "金", "土", "日"]
    if any(w in s for w in weekdays):
        # 一番近いその曜日を探す（今日以降）
        for i in range(7):
            d = today + timedelta(days=i)
            if weekdays[d.weekday()] in s:
                return d.isoformat()

    # 不明 → None
    return None
