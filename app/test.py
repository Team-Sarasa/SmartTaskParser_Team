from datetime import date
from app.notion_client import create_notion_task

page_id = create_notion_task(
    title="テストタスク from スクリプト",
    due_date=date.today(),
    priority="medium",
    notes="メモのテスト",
    source="local",
)

print("created page:", page_id)

