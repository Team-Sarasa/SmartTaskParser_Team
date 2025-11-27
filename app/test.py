from app.task_service import create_task_from_text

if __name__ == "__main__":
    task = create_task_from_text(
        "明日の午前までに研究のスライド直す",
        source="local",
        user_id="debug-user",
    )
    print(task)
    print("Task created successfully.")