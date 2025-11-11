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

@app.route("/", methods=["GET"])
def index():
    search_query = request.args.get("query", "").strip()
    query = MyTask.query

    # Grab filters 
    rating_filter = [r for r in request.args.getlist("rating") if r.strip()]
    type_filter = request.args.get("type")
    service_filter = [s for s in request.args.getlist("service") if s.strip()]
    genre_filter = [g for g in request.args.getlist("genre") if g.strip()]

    has_filters = bool(rating_filter or type_filter or service_filter or genre_filter)
    tasks = []

    if search_query or has_filters:
        # Search term logic
        if search_query:
            terms = [term.strip().lower() for term in search_query.replace(",", " ").split() if term.strip()]
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

        # Filter logic
        if genre_filter:
            query = query.filter(or_(*[MyTask.listed_in.ilike(f"%{genre}%") for genre in genre_filter]))
        if rating_filter:
            query = query.filter(or_(*[MyTask.rating.ilike(f"%{rating}%") for rating in rating_filter]))
        if type_filter and type_filter.strip():
            query = query.filter(MyTask.type.ilike(f"%{type_filter}%"))
        if service_filter:
            query = query.filter(or_(*[MyTask.service.ilike(f"%{service}%") for service in service_filter]))

        tasks = query.all()

    return render_template(
        "index.html",
        tasks=tasks,
        query=search_query,
        selected_genres=genre_filter,
        selected_ratings=rating_filter,
        selected_type=type_filter,
        selected_services=service_filter
    )



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