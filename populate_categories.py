from app import create_app, db
from models import Category

app = create_app()

with app.app_context():
    categories = [
        {'name': 'Classroom', 'short_name': 'classroom'},
        {'name': 'Church', 'short_name': 'church'},
        {'name': 'Cultural', 'short_name': 'cultural'},
        {'name': 'Court', 'short_name': 'court'},
        {'name': 'Community', 'short_name': 'community'}
    ]

    for category_data in categories:
        category = Category(
            name=category_data['name'],
            short_name=category_data['short_name']
        )
        db.session.add(category)

    db.session.commit()
