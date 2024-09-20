from app import create_app, db
from models import Event, Category, Organizer
from datetime import date

app = create_app()

with app.app_context():
    category = Category.query.filter_by(name='Church').first()

    organizer = Organizer.query.filter_by(name='College of Computer Studies').first()

    long_html_content = """
    <p>On August 19, 2024, from 7:30 AM to 9:00 AM, I attended the CCS
    Opening Devotion at Silliman University Church as a participant, where I
    joined my fellow College of Computer Studies students in a meaningful
    gathering. The objective of the event was to deepen our spiritual
    connection and to remind us of the importance of faith in our daily lives
    as students.</p>
    <p>When I first arrived, I didn’t know how the event would go or what
    kind of impact it would have on me. However, my expectations changed as
    I listened to Rev. Iris H. Tibus, whose words left a lasting impression.
    She explained the meaning of CCS, emphasizing that it stands for
    <strong>C</strong>ommitting all plans and activities to God,
    <strong>C</strong>onnecting with God in prayer, and
    <strong>S</strong>urrendering all glory and credit to God. This stuck
    with me, as it aligns with my own values and the way I approach
    challenges in life. The most impactful part of the event was hearing
    this message, which reinforced my belief that with God by my side, I can
    face any obstacle with courage and determination.</p>
    <p>This experience has changed my perspective on challenges, making me
    see them as obstacles that I will inevitably overcome because I know
    that God is always with me. It has also inspired me to uphold these
    values and share them with my peers, especially those who may be
    struggling or feeling lost. The event served as a reminder that even
    during the busy Hibalag Week, Sillimanians remain devoted to their
    faith, never forgetting to make time for God.</p>
    <p>Because of this activity, I am better than who I was
    yesterday, I now have a greater sense of self-trust and confidence,
    knowing that God is always supporting me.</p>
    """
    
    long_proof = """
    <div><figure><img src="ccs-opening-devotion-proof.png" alt="CCS Opening Devotion Proof"><figcaption>Proof</figcaption></figure></div>
    """

    thumbnail_path = '../static/ccs-opening-devotion.png'

    event = Event(
        name='CCS Opening Devotion',
        short_name='ccs-opening-devotion',
        date=date(2024, 8, 19),
        venue='Silliman University Church',
        points=1,
        reflection=long_html_content,
        category_id=category.id,
        organizer_id=organizer.id,
        thumbnail=thumbnail_path,
        proof=long_proof
    )

    db.session.add(event)
    db.session.commit()
