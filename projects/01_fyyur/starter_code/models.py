from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class Show(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    artist_id = db.Column(db.Integer, db.ForeignKey("artist.id"), nullable=False)
    venue_id = db.Column(db.Integer, db.ForeignKey("venue.id"), nullable=False)
    start_time = db.Column(db.DateTime, nullable=False)


class Venue(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    city = db.Column(db.String(120), nullable=False)
    state = db.Column(db.String(120), nullable=False)
    address = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(120))
    genres = db.Column(db.String(500), nullable=False)
    image_link = db.Column(
        db.String(500),
        nullable=False,
        default="https://www.kkl-luzern.ch/media/wysiwyg/image_gallery/Event/Lucerne_Hall/LuzernerSaal_01.jpg",
    )
    facebook_link = db.Column(db.String(120))
    website_link = db.Column(db.String(120))
    seeking_talent = db.Column(db.Boolean, nullable=False, default=False)
    seeking_description = db.Column(db.String(120), nullable=False, default="")
    artists = db.relationship(
        "Artist", secondary="show", backref=db.backref("venue", lazy=True)
    )
    shows = db.relationship("Show", backref="venue", lazy=True)


class Artist(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    city = db.Column(db.String(120), nullable=False)
    state = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(120))
    genres = db.Column(db.String(500), nullable=False)
    image_link = db.Column(
        db.String(500),
        nullable=False,
        default="https://lh3.googleusercontent.com/proxy/oLjqpuZxpQiOlySHcOv6jF4qUvbu4iieBM27cenWxa2fF9_YAIBk1wJzx42RQHV356bItriCGTbyE-9IEvc4EOz9sN7JVQ",
    )
    facebook_link = db.Column(db.String(120))
    website_link = db.Column(db.String(120))
    seeking_venue = db.Column(db.Boolean, nullable=False, default=False)
    seeking_description = db.Column(db.String(120), nullable=False, default="")
    vanues = db.relationship(
        "Venue", secondary="show", backref=db.backref("venue", lazy=True)
    )
    shows = db.relationship("Show", backref="artist", lazy=True)
