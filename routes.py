from flask import render_template, request, abort
from models import Category, Event

def register_routes(app, db):
    @app.route("/")
    def home():
        return render_template("index.html")

    @app.route('/<category>')
    def category_page(category):
        category = Category.query.filter_by(short_name=category).first()

        if not category:
            abort(404, description="Category not found")

        events = category.events

        return render_template("category.html", category=category, events=events)

    @app.route('/<category>/<event>')
    def event_page(category, event):
        category = Category.query.filter_by(short_name=category).first()

        if not category:
            abort(404, description="Category not found")

        event = Event.query.filter_by(short_name=event, category_id=category.id).first()

        if not event:
            abort(404, description="Event not found")

        organizer = event.organizer

        if not organizer:
            abort(404, description="Organizer not found for this event")

        date = event.date.strftime("%B %d, %Y")

        return render_template("reflection.html", category=category, event=event, organizer=organizer, date=date)
