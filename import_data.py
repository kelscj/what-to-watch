import pandas as pd
from app import db, MyTask, app

df = pd.read_csv("streaming_dataset.csv")
df.fillna('', inplace=True)

with app.app_context():
    db.create_all()  # Ensure DB exists before import

    success_count = 0
    error_count = 0

    for idx, row in df.iterrows():
        try:
            task = MyTask(
                show_id =int(row['show_id']),
                type=row['type'],
                title=row['title'],
                director=row['director'],
                cast=row['cast'],
                country=row['country'],
                date_added=row['date_added'],
                release_year=int(row['release_year']),
                rating=row['rating'],
                duration=row['duration'],
                listed_in=row['listed_in'],
                description=row['description'],
                service=row['service']
            )
            
            db.session.add(task)
            success_count += 1

        except Exception as e:
            error_count += 1
            print(f"❌ [Row {idx}] Skipped because: {e}")
            print("   Row data:", row.to_dict())

    db.session.commit()
    print(f"\n✅ Import Complete!\nAdded: {success_count} movies\nSkipped: {error_count} rows\n")
    db.create_all()