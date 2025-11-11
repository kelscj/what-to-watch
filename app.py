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
    show_id = db.Column(db.String(500), primary_key=True)
    type = db.Column(db.String(500), nullable=True)
    title = db.Column(db.String(500), nullable=False)
    director = db.Column(db.String(500), nullable=True)
    cast = db.Column(db.String(1000), nullable=True)
    country = db.Column(db.String(500), nullable=True)
    date_added = db.Column(db.String(100), nullable=True)
    release_year = db.Column(db.Integer, nullable=True)
    rating = db.Column(db.String(100), nullable=True)
    duration = db.Column(db.String(100), nullable=True)
    listed_in = db.Column(db.String(500), nullable=True)
    description = db.Column(db.Text, nullable=True)
    service = db.Column(db.String(100), nullable=False)

    def __repr__(self):
        return f"<Movie {self.title}>"

# Home page – display all entries
@app.route("/", methods=["GET"])
def index():
    search_query = request.args.get("query", "").strip()
    tasks = []
    query = MyTask.query

    if search_query:
        # Split on commas or whitespace, remove empty terms
        terms = [term.strip().lower() for term in search_query.replace(",", " ").split() if term.strip()]
        
        # Filter so each term must appear in either genres, keywords, cast, or title
        for term in terms:
            like_term = f"%{term}%"
            query = query.filter(
                or_(
                    MyTask.listed_in.ilike(like_term),
                    MyTask.description.ilike(like_term),
                    MyTask.title.ilike(like_term),
                    MyTask.cast.ilike(like_term),
                    MyTask.director.ilike(like_term)
                )
            )

        # Apply additional filters from form inputs
        rating_filter = request.args.getlist("rating")
        type_filter = request.args.get("type")
        service_filter = request.args.getlist("service")
        genre_filter = request.args.getlist("genre")


        # Apply filters if selected
        if genre_filter:
            query = query.filter(or_(*[MyTask.service.ilike(f"%{genre}%") for genre in genre_filter ]))
        if rating_filter:
            query = query.filter(or_(*[MyTask.service.ilike(f"%{rating}%") for rating in rating_filter ]))
        if type_filter:
            query = query.filter(MyTask.type.ilike(f"%{type_filter}%"))
        if service_filter:
            query = query.filter(or_(*[MyTask.service.ilike(f"%{service}%") for service in service_filter ]))

        tasks = query.all()

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