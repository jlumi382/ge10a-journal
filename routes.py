from flask import render_template, request, abort, redirect, url_for, session
from auth import auth, ADMIN_USERNAME, ADMIN_PASSWORD
from models import Category, Event, Organizer
from functools import wraps
from datetime import datetime
import os
from werkzeug.utils import secure_filename

folders = {
    'ORGANIZERS_FOLDER': 'static/uploads/organizers',
    'THUMBNAILS_FOLDER': 'static/uploads/thumbnails',
    'PROOF_FOLDER': 'static/uploads/proof'
}

for folder_name, folder_path in folders.items():
    os.makedirs(folder_path, exist_ok=True)

ORGANIZERS_FOLDER = folders['ORGANIZERS_FOLDER']
THUMBNAILS_FOLDER = folders['THUMBNAILS_FOLDER']
PROOF_FOLDER = folders['PROOF_FOLDER']
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'logged_in' not in session:
            return redirect(url_for('admin'))
        return f(*args, **kwargs)
    return decorated_function

def register_routes(app, db):
    @app.route("/")
    def home():
        return render_template("index.html")

    @app.route('/<category>')
    def category_page(category):
        category = Category.query.filter_by(short_name=category).first()

        if not category:
            abort(404, description="Category not found.")

        events = Event.query.filter_by(category_id=category.id)

        return render_template("category.html", category=category, events=events)

    @app.route('/<category>/<event_id>')
    def event_page(category, event_id):
        category = Category.query.filter_by(short_name=category).first()

        if not category:
            abort(404, description="Category not found.")

        event = Event.query.filter_by(id=event_id, category_id=category.id).first()

        if not event:
            abort(404, description="Event not found.")

        organizer = event.organizer

        if not organizer:
            abort(404, description="Organizer not found.")

        date = event.date.strftime("%B %-d, %Y")

        return render_template("reflection.html", category=category, event=event, organizer=organizer, date=date)

    @auth.verify_password
    def verify_password(username, password):
        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            return True
        return False

    @app.route('/admin')
    @auth.login_required
    def admin():
        session['logged_in'] = True
        return render_template("admin.html")

    @app.route('/admin/add')
    @login_required
    def add_options():
        return render_template('add_options.html')

    @app.route('/admin/add/category', methods=['GET', 'POST'])
    @login_required
    def add_category():
        if request.method == 'POST':
            name = request.form.get('name')

            if not name:
                return render_template('category_form.html', error="Category name is required.")

            new_category = Category(name=name, short_name=name.lower())
            db.session.add(new_category)
            db.session.commit()

            return redirect(url_for('add_options'))

        return render_template('category_form.html')

    @app.route('/admin/add/organizer', methods=['GET', 'POST'])
    @login_required
    def add_organizer():
        if request.method == 'POST':
            name = request.form.get('name')
            short_name = request.form.get('short_name')
            logo = request.files.get('logo')

            if not name:
                return render_template('organizer_form.html', error="Organizer name is required.")

            if not logo or not allowed_file(logo.filename):
                return render_template('organizer_form.html', error="Logo is required and must be a valid file type.")

            logo_filename = secure_filename(logo.filename)
            logo_path = os.path.join(app.root_path, ORGANIZERS_FOLDER, logo_filename)
            logo.save(logo_path)

            if not os.path.exists(logo_path):
                return render_template('organizer_form.html', error="Logo file not uploaded successfully.")

            new_organizer = Organizer(name=name, short_name=short_name.lower(), logo=logo_filename)
            db.session.add(new_organizer)
            db.session.commit()

            return redirect(url_for('add_options'))

        return render_template('organizer_form.html')

    @app.route('/admin/add/event', methods=['GET', 'POST'])
    @login_required
    def add_event():
        organizers = Organizer.query.all()
        categories = Category.query.all()

        if request.method == 'POST':
            name = request.form.get('name')
            short_name = request.form.get('short_name')
            date = request.form.get('date')
            venue = request.form.get('venue')
            points = request.form.get('points')
            reflection = request.form.get('reflection')
            category_id = request.form.get('category_id')
            organizer_id = request.form.get('organizer_id')

            thumbnail = request.files.get('thumbnail')
            proof = request.files.get('proof')

            if not all([name, short_name, date, venue, points, reflection, category_id, organizer_id, thumbnail, proof]):
                return render_template('event_form.html', error="All fields are required.", categories=categories, organizers=organizers)

            try:
                points = int(points)
            except ValueError:
                return render_template('event_form.html', error="Points must be an integer.", categories=categories, organizers=organizers)

            if points < 1 or points > 4:
                return render_template('event_form.html', error="Points must be from 1 to 4.", categories=categories, organizers=organizers)

            if thumbnail and allowed_file(thumbnail.filename):
                thumbnail_filename = secure_filename(thumbnail.filename)
                thumbnail_path = os.path.join(app.root_path, THUMBNAILS_FOLDER, thumbnail_filename)
                thumbnail.save(thumbnail_path)
                
                if not os.path.exists(thumbnail_path):
                    return render_template('event_form.html', error="Thumbnail file not uploaded successfully.", categories=categories, organizers=organizers)

            if proof and allowed_file(proof.filename):
                proof_filename = secure_filename(proof.filename)
                proof_path = os.path.join(app.root_path, PROOF_FOLDER, proof_filename)
                proof.save(proof_path)

                if not os.path.exists(proof_path):
                    return render_template('event_form.html', error="Proof file not uploaded successfully.", categories=categories, organizers=organizers)

            new_event = Event(
                name=name,
                short_name=short_name.lower(),
                date=datetime.strptime(date, "%Y-%m-%d").date(),
                venue=venue,
                points=points,
                reflection=reflection,
                category_id=category_id,
                organizer_id=organizer_id,
                thumbnail=thumbnail_filename,
                proof=proof_filename
            )

            db.session.add(new_event)
            db.session.commit()

            return redirect(url_for('add_options'))

        return render_template('event_form.html', categories=categories, organizers=organizers)

    @app.route('/admin/edit')
    @login_required
    def edit_options():
        return render_template('edit_options.html')

    @app.route('/admin/edit/category')
    @login_required
    def editable_categories():
        categories = Category.query.all()
        return render_template('editable_categories.html', categories=categories)

    @app.route('/admin/edit/organizer')
    @login_required
    def editable_organizers():
        organizers = Organizer.query.all()
        return render_template('editable_organizers.html', organizers=organizers)

    @app.route('/admin/edit/event')
    @login_required
    def editable_events():
        events = Event.query.all()
        return render_template('editable_events.html', events=events)

    @app.route('/admin/edit/category/<category_id>', methods=['GET', 'POST'])
    @login_required
    def edit_category(category_id):
        category = Category.query.filter_by(id=category_id).first()

        if not category:
            abort(404, description="Category not found.")

        if request.method == 'POST':
            name = request.form['name']
            short_name = name.lower()

            if not all([name, short_name]):
                return render_template('category_form.html', error="All fields are required.")

            category.name = name
            category.short_name = short_name

            db.session.commit()

            return redirect(url_for('editable_categories'))

        return render_template('category_form.html', category=category)

    @app.route('/admin/edit/organizer/<organizer_id>', methods=['GET', 'POST'])
    @login_required
    def edit_organizer(organizer_id):
        organizer = Organizer.query.filter_by(id=organizer_id).first()

        if not organizer:
            abort(404, description="Organizer not found.")

        if request.method == 'POST':
            name = request.form['name']
            logo = request.files.get('logo')

            if logo and allowed_file(logo.filename):
                logo_filename = secure_filename(logo.filename)
                logo_path = os.path.join(app.root_path, ORGANIZERS_FOLDER, logo_filename)
                logo.save(logo_path)

                if not os.path.exists(logo_path):
                    return render_template('organizer_form.html', error="Logo file not uploaded successfully.", organizer=organizer)

            if organizer.logo:
                logo_path = os.path.join(app.root_path, ORGANIZERS_FOLDER, organizer.logo)
                if os.path.exists(logo_path):
                    os.remove(logo_path)

            organizer.logo = logo_filename

            organizer.name = name

            db.session.commit()

            return redirect(url_for('editable_organizers'))

        return render_template('organizer_form.html', organizer=organizer)

    @app.route('/admin/edit/event/<event_id>', methods=['GET', 'POST'])
    @login_required
    def edit_event(event_id):
        event = Event.query.filter_by(id=event_id).first()
        categories = Category.query.all()
        organizers = Organizer.query.all()

        if not event:
            abort(404, description="Event not found.")

        if request.method == 'POST':
            name = request.form['name']
            short_name = request.form['short_name']
            date = request.form['date']
            venue = request.form['venue']
            points = request.form['points']
            reflection = request.form['reflection']
            category_id = request.form['category_id']
            organizer_id = request.form['organizer_id']

            thumbnail = request.files['thumbnail']
            proof = request.files['proof']

            if not all([name, short_name, date, venue, points, reflection, category_id, organizer_id]):
                return render_template('event_form.html', error="All fields are required.", categories=categories, organizers=organizers)

            try:
                points = int(points)
            except ValueError:
                return render_template('event_form.html', error="Points must be an integer.", categories=categories, organizers=organizers)

            if points < 1 or points > 4:
                return render_template('event_form.html', error="Points must be from 1 to 4.", categories=categories, organizers=organizers)

            if thumbnail and allowed_file(thumbnail.filename):
                thumbnail_filename = secure_filename(thumbnail.filename)
                thumbnail_path = os.path.join(app.root_path, THUMBNAILS_FOLDER, thumbnail_filename)
                thumbnail.save(thumbnail_path)
                
                if not os.path.exists(thumbnail_path):
                    return render_template('event_form.html', error="Thumbnail file not uploaded successfully.", event=event, categories=categories, organizers=organizers)

            if proof and allowed_file(proof.filename):
                proof_filename = secure_filename(proof.filename)
                proof_path = os.path.join(app.root_path, PROOF_FOLDER, proof_filename)
                proof.save(proof_path)

                if not os.path.exists(proof_path):
                    return render_template('event_form.html', error="Proof file not uploaded successfully.", event=event, categories=categories, organizers=organizers)

            if event.thumbnail:
                thumbnail_path = os.path.join(app.root_path, THUMBNAILS_FOLDER, event.thumbnail)
                if os.path.exists(thumbnail_path):
                    os.remove(thumbnail_path)

            if event.proof:
                proof_path = os.path.join(app.root_path, PROOF_FOLDER, event.proof)
                if os.path.exists(proof_path):
                    os.remove(proof_path)

            event.name = name
            event.short_name = short_name.lower()
            event.date = datetime.strptime(date, "%Y-%m-%d").date()
            event.venue = venue
            event.points = points
            event.reflection = reflection
            event.category_id = category_id
            event.organizer_id = organizer_id

            db.session.commit()

            return redirect(url_for('editable_events'))

        return render_template('event_form.html', event=event, categories=categories, organizers=organizers)

    @app.route('/admin/delete/category/<category_id>', methods=['POST'])
    @login_required
    def delete_category(category_id):
        category = Category.query.filter_by(id=category_id).first()

        if not category:
            abort(404, description="Category not found.")

        db.session.delete(category)
        db.session.commit()

        return redirect(url_for('editable_categories'))

    @app.route('/admin/delete/organizer/<organizer_id>', methods=['POST'])
    @login_required
    def delete_organizer(organizer_id):
        organizer = Organizer.query.filter_by(id=organizer_id).first()

        if not organizer:
            abort(404, description="Organizer not found.")

        if organizer.logo:
            logo_path = os.path.join(app.root_path, ORGANIZERS_FOLDER, organizer.logo)
            if os.path.exists(logo_path):
                os.remove(logo_path)

        db.session.delete(organizer)
        db.session.commit()

        return redirect(url_for('editable_organizers'))

    @app.route('/admin/delete/event/<event_id>', methods=['POST'])
    @login_required
    def delete_event(event_id):
        event = Event.query.filter_by(id=event_id).first()

        if not event:
            abort(404, description="Event not found.")

        if event.thumbnail:
            thumbnail_path = os.path.join(app.root_path, THUMBNAILS_FOLDER, event.thumbnail)
            if os.path.exists(thumbnail_path):
                os.remove(thumbnail_path)

        if event.proof:
            proof_path = os.path.join(app.root_path, PROOF_FOLDER, event.proof)
            if os.path.exists(proof_path):
                os.remove(proof_path)

        db.session.delete(event)
        db.session.commit()

        return redirect(url_for('editable_events'))

    @app.route('/admin/logout')
    @login_required
    def logout():
        session.pop('logged_in', None)
        return redirect(url_for('admin'))
    
    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('404.html', description=e.description), 404
