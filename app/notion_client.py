import os
from datetime import date
from typing import Any, Dict, Optional

from dotenv import load_dotenv
from notion_client import Client


# .env から環境変数読み込み
load_dotenv()

NOTION_API_KEY = os.getenv("NOTION_API_KEY")
NOTION_DATABASE_ID = os.getenv("NOTION_DATABASE_ID")

if not NOTION_API_KEY:
    raise ValueError("Environment variable NOTION_API_KEY is not set.")
if not NOTION_DATABASE_ID:
    raise ValueError("Environment variable NOTION_DATABASE_ID is not set.")

# Notion クライアント初期化
notion = Client(auth=NOTION_API_KEY)


def create_notion_task(
    title: str,
    due_date: Optional[date],
    priority: str,
    notes: Optional[str],
    source: str = "line",
) -> str:
    """
    Notion のタスク用データベースに 1 件タスクを登録する。

    Args:
        title: タスク名
        due_date: 期限（日付オブジェクト。None の場合は未設定）
        priority: "low" | "medium" | "high"
        notes: メモ（任意）
        source: "line" や "web" など、どこから来たタスクか

    Returns:
        作成された Notion ページの ID（文字列）
    """
    properties: Dict[str, Any] = {
        # タイトル (Title プロパティ)
        "Title": {
            "title": [
                {
                    "text": {
                        "content": title,
                    }
                }
            ]
        },
        # ステータス (Select) - デフォルトは「未着手」
        "Status": {
            "status": {
                "name": "未着手",
            }
        },
        # 優先度 (Select)
        "Priority": {
            "select": {
                "name": priority_to_notion(priority),
            }
        },
    }

    # 期限 (Date)
    if due_date:
        properties["Due"] = {
            "date": {
                "start": due_date.isoformat(),
            }
        }

    # メモ (RichText)
    if notes:
        properties["Notes"] = {
            "rich_text": [
                {
                    "text": {
                        "content": notes,
                    }
                }
            ]
        }

    page = notion.pages.create(
        parent={"database_id": NOTION_DATABASE_ID},
        properties=properties,
    )

    # page["id"] は "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx" 形式
    return page["id"]


def priority_to_notion(priority: str) -> str:
    """
    内部表現の priority を Notion の Select 名に変換する。
    Notion 側の選択肢名に合わせること。
      - low    -> "低"
      - medium -> "中"
      - high   -> "高"
    想定外の値が来たら "中" 扱いにする。
    """
    mapping = {
        "low": "低",
        "medium": "中",
        "high": "高",
    }
    return mapping.get(priority, "中")
