import pandas as pd
from app import db, MyTask, app

df = pd.read_csv("streaming_dataset.csv")
df = df.fillna("")

def safe_int(value):
    try:
        return int(value)
    except (ValueError, TypeError):
        return None

with app.app_context():
    db.create_all()

    success_count = 0
    error_count = 0

    for idx, row in enumerate(df.to_dict(orient="records")):
        try:
            task = MyTask()

            task.show_id = safe_int(row.get("show_id"))
            task.type = row.get("type", "")
            task.title = row.get("title", "")
            task.director = row.get("director", "")
            task.cast = row.get("cast", "")
            task.country = row.get("country", "")
            task.date_added = row.get("date_added", "")
            task.release_year = safe_int(row.get("release_year"))
            task.rating = row.get("rating", "")
            task.duration = row.get("duration", "")
            task.listed_in = row.get("listed_in", "")
            task.description = row.get("description", "")
            task.service = row.get("service", "")

            db.session.add(task)
            success_count += 1

        except Exception as e:
            error_count += 1
            print(f"[Row {idx}] Skipped because: {e}")
            print("Row data:", row)

    db.session.commit()

    print(
        f"\nImport complete.\n"
        f"Rows added: {success_count}\n"
        f"Rows skipped: {error_count}\n"
    )
