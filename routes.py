from flask import render_template, request, abort
from models import Category, Event

def register_routes(app, db):
    # Home route
    @app.route("/")
    def home():
        return render_template("index.html")

    # Dynamic category page route
    @app.route('/<category>')
    def category_page(category):
        # Query the category by name
        category = Category.query.filter_by(name=category).first()

        # If category doesn't exist, return a 404 error
        if not category:
            abort(404, description="Category not found")

        # Get all events related to this category
        events = category.events

        # Render the category page with its events
        return render_template("category.html", category=category, events=events)

    # Dynamic event page route
    @app.route('/<category>/<event>')
    def event_page(category, event):
        # Query the category by name
        category = Category.query.filter_by(name=category).first()

        # If category doesn't exist, return a 404 error
        if not category:
            abort(404, description="Category not found")

        # Query the event by name and ensure it belongs to the correct category
        event = Event.query.filter_by(name=event, category_id=category.id).first()

        # If event doesn't exist, return a 404 error
        if not event:
            abort(404, description="Event not found")

        # Render the event page with its details
        return render_template("reflection.html", category=category, event=event)