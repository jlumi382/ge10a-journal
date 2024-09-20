from app import create_app, db
from models import Organizer

app = create_app()

with app.app_context():
    logo_path = '../static/ccs.png'

    organizer = Organizer(
        name='College of Computer Studies',
        logo=logo_path
    )

    db.session.add(organizer)
    db.session.commit()
