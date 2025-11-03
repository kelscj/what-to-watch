import pandas as pd
from app import db, MyTask, app

df = pd.read_csv("movie_data.csv")
df.fillna('', inplace=True)

def to_bool(value):
    # Convert CSV adult field to true boolean
    return str(value).strip().lower() in ("true", "1", "yes")

with app.app_context():
    db.create_all()  # Ensure DB exists before import

    success_count = 0
    error_count = 0

    for idx, row in df.iterrows():
        try:
            task = MyTask(
                title=row['title'],
                vote_average=float(row['vote_average']),
                status=row['status'],
                release_date=row['release_date'],
                revenue=float(row['revenue']),
                runtime=int(row['runtime']),
                adult=to_bool(row['adult']),
                budget=float(row['budget']),
                original_language=row['original_language'],
                overview=row['overview'],
                popularity=float(row['popularity']),
                tagline=row['tagline'],
                genres=row['genres'],
                production_companies=row['production_companies'],
                keywords=row['keywords']
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