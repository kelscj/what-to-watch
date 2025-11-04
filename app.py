from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy
from flask_scss import Scss
from datetime import datetime
from sqlalchemy import or_


# Initialize app
app = Flask(__name__)
Scss(app)

# Config
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///database.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Database
db = SQLAlchemy(app)

# Model
class MyTask(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(500), nullable=False)
    vote_average = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(500), nullable=False)
    release_date = db.Column(db.String(500), nullable=False)
    revenue = db.Column(db.Float, nullable=False)
    runtime = db.Column(db.Integer, nullable=False)
    adult = db.Column(db.Boolean, nullable=False)
    budget = db.Column(db.Float, nullable=False)
    original_language = db.Column(db.String(500), nullable=False)
    overview = db.Column(db.Text, nullable=False)
    popularity = db.Column(db.Float, nullable=False)
    tagline = db.Column(db.String(500), nullable=True)
    genres = db.Column(db.String(500), nullable=True)
    production_companies = db.Column(db.String(500), nullable=True)
    keywords = db.Column(db.String(500), nullable=True)

    def __repr__(self):
        return f"<Movie {self.title}>"

# Home page – display all entries
@app.route("/", methods=["GET"])
def index():
    search_query = request.args.get("query", "").strip()
    tasks = []

    if search_query:
        # Split on commas or whitespace, remove empty terms
        terms = [term.strip().lower() for term in search_query.replace(",", " ").split() if term.strip()]

        # Start with all non-adult movies
        query = MyTask.query.filter(MyTask.adult.is_(False))

        # Filter so each term must appear in either genres or keywords (AND logic)
        for term in terms:
            like_term = f"%{term}%"
            query = query.filter(
                or_(
                    MyTask.genres.ilike(like_term),
                    MyTask.keywords.ilike(like_term)
                )
            )

        # Apply additional filters from form inputs
        genre_filter = request.args.get("genre", "").strip()
        runtime_filter = request.args.get("runtime", type=int)

        # Apply filters if selected
        if genre_filter:
            query = query.filter(MyTask.genres.ilike(f"%{genre_filter}%"))

        if runtime_filter:
            query = query.filter(MyTask.runtime <= runtime_filter)

        # Always exclude adult content
        query = query.filter(MyTask.adult.is_(False))

        tasks = query.order_by(MyTask.vote_average.desc()).all()

    return render_template("index.html", tasks=tasks, query=search_query)


# Delete route (optional, only if needed)
@app.route("/delete/<int:id>")
def delete(id):
    task = MyTask.query.get_or_404(id)
    try:
        db.session.delete(task)
        db.session.commit()
        return redirect("/")
    except Exception as e:
        return f"ERROR deleting: {e}"

# Add edit/view routes as needed...

# Ensure DB is created
if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)