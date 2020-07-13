# ----------------------------------------------------------------------------#
# Imports
# ----------------------------------------------------------------------------#

import sys
import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_migrate import Migrate
from sqlalchemy import func
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *

# ----------------------------------------------------------------------------#
# App Config.
# ----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object("config")
db = SQLAlchemy(app)
migrate = Migrate(app, db)

# ----------------------------------------------------------------------------#
# Models.
# ----------------------------------------------------------------------------#


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


# ----------------------------------------------------------------------------#
# Filters.
# ----------------------------------------------------------------------------#


def format_datetime(value, format="medium"):
    date = dateutil.parser.parse(value)
    if format == "full":
        format = "EEEE MMMM, d, y 'at' h:mma"
    elif format == "medium":
        format = "EE MM, dd, y h:mma"
    return babel.dates.format_datetime(date, format)


app.jinja_env.filters["datetime"] = format_datetime

# ----------------------------------------------------------------------------#
# Controllers.
# ----------------------------------------------------------------------------#


@app.route("/")
def index():
    return render_template("pages/home.html")


#  Venues
#  ----------------------------------------------------------------


@app.route("/venues")
def venues():
    areas = Venue.query.with_entities(
        Venue.city, Venue.state, func.count(Venue.id)
    ).group_by(Venue.city, Venue.state)

    data = []
    for area in areas:
        city = area[0]
        state = area[1]
        venues_for_area = Venue.query.filter_by(city=city).filter_by(state=state).all()
        venues_by_location = {
            "city": city,
            "state": state,
            "venues": [{"id": v.id, "name": v.name,} for v in venues_for_area],
        }
        data.append(venues_by_location)
    return render_template("pages/venues.html", areas=data)


@app.route("/venues/search", methods=["POST"])
def search_venues():
    search_term = request.form.get("search_term", "")
    results = Venue.query.filter(Venue.name.ilike(f"%{search_term}%")).all()
    data = [{"id": result.id, "name": result.name} for result in results]
    response = {"count": len(results), "data": data}

    return render_template(
        "pages/search_venues.html",
        results=response,
        search_term=request.form.get("search_term", ""),
    )


@app.route("/venues/<int:venue_id>")
def show_venue(venue_id):
    data = Venue.query.get(venue_id)
    data.genres = data.genres.split(",")
    past_shows = get_venues_shows(venue_id)
    data.past_shows = past_shows
    data.past_shows_count = len(past_shows)
    upcoming_shows = get_venues_shows(venue_id, True)
    data.upcoming_shows = upcoming_shows
    data.upcoming_shows_count = len(upcoming_shows)
    return render_template("pages/show_venue.html", venue=data)


def get_venues_shows(venue_id, upcoming=False):
    shows_records = (
        Show.query.join(Artist)
        .filter(Show.venue_id == venue_id)
        .filter(
            Show.start_time < datetime.now()
            if not upcoming
            else Show.start_time >= datetime.now()
        )
        .all()
    )
    shows = [
        {
            "artist_id": show.artist_id,
            "artist_name": show.artist.name,
            "artist_image_link": show.artist.image_link,
            "start_time": show.start_time.strftime("%Y-%m-%d %H:%M:%S"),
        }
        for show in shows_records
    ]
    return shows


#  Create Venue
@app.route("/venues/create", methods=["GET"])
def create_venue_form():
    form = VenueForm()
    return render_template("forms/new_venue.html", form=form)


@app.route("/venues/create", methods=["POST"])
def create_venue_submission():
    error = False
    try:
        name = request.form.get("name")
        city = request.form.get("city")
        state = request.form.get("state")
        address = request.form.get("address")
        phone = request.form.get("phone")
        genres = request.form.getlist("genres")
        comma_separated_genres = ",".join(genres)
        image_link = request.form.get("image_link")
        facebook_link = request.form.get("facebook_link")
        website_link = request.form.get("website_link")
        seeking_talent = True if "seeking_talent" in request.form else False
        seeking_description = request.form.get("seeking_description")
        venue = Venue(
            name=name,
            city=city,
            state=state,
            address=address,
            phone=phone,
            genres=comma_separated_genres,
            image_link=image_link,
            facebook_link=facebook_link,
            website_link=website_link,
            seeking_talent=seeking_talent,
            seeking_description=seeking_description,
        )
        db.session.add(venue)
        db.session.commit()
    except:
        error = True
        db.session.rollback()
        print(sys.exc_info())
    finally:
        db.session.close()
    if error:
        flash(
            "An error occurred. Venue " + request.form["name"] + " could not be listed."
        )
    if not error:
        flash("Venue " + request.form["name"] + " was successfully listed!")
        return render_template("pages/home.html")


# End Create Venue


@app.route("/venues/<venue_id>", methods=["DELETE"])
def delete_venue(venue_id):
    # TODO: Complete this endpoint for taking a venue_id, and using
    # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.

    # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
    # clicking that button delete it from the db then redirect the user to the homepage
    return None


#  Artists
#  ----------------------------------------------------------------
@app.route("/artists")
def artists():
    data = Artist.query.order_by("name").all()
    return render_template("pages/artists.html", artists=data)


@app.route("/artists/search", methods=["POST"])
def search_artists():
    search_term = request.form.get("search_term", "")
    results = Artist.query.filter(Artist.name.ilike(f"%{search_term}%")).all()
    data = [{"id": result.id, "name": result.name} for result in results]
    response = {"count": len(results), "data": data}

    return render_template(
        "pages/search_artists.html", results=response, search_term=search_term
    )


@app.route("/artists/<int:artist_id>")
def show_artist(artist_id):
    data = Artist.query.get(artist_id)
    data.genres = data.genres.split(",")
    past_shows = get_artist_shows(artist_id)
    data.past_shows = past_shows
    data.past_shows_count = len(past_shows)
    upcoming_shows = get_artist_shows(artist_id, True)
    data.upcoming_shows = upcoming_shows
    data.upcoming_shows_count = len(upcoming_shows)
    return render_template("pages/show_artist.html", artist=data)


def get_artist_shows(artist_id, upcoming=False):
    shows_records = (
        Show.query.join(Venue)
        .filter(Show.artist_id == artist_id)
        .filter(
            Show.start_time < datetime.now()
            if not upcoming
            else Show.start_time >= datetime.now()
        )
        .all()
    )
    shows = [
        {
            "venue_id": show.venue_id,
            "venue_name": show.venue.name,
            "venue_image_link": show.venue.image_link,
            "start_time": show.start_time.strftime("%Y-%m-%d %H:%M:%S"),
        }
        for show in shows_records
    ]
    return shows


#  Update
#  ----------------------------------------------------------------
@app.route("/artists/<int:artist_id>/edit", methods=["GET"])
def edit_artist(artist_id):
    form = ArtistForm()
    artist = {
        "id": 4,
        "name": "Guns N Petals",
        "genres": ["Rock n Roll"],
        "city": "San Francisco",
        "state": "CA",
        "phone": "326-123-5000",
        "website": "https://www.gunsnpetalsband.com",
        "facebook_link": "https://www.facebook.com/GunsNPetals",
        "seeking_venue": True,
        "seeking_description": "Looking for shows to perform at in the San Francisco Bay Area!",
        "image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80",
    }
    # TODO: populate form with fields from artist with ID <artist_id>
    return render_template("forms/edit_artist.html", form=form, artist=artist)


@app.route("/artists/<int:artist_id>/edit", methods=["POST"])
def edit_artist_submission(artist_id):
    # TODO: take values from the form submitted, and update existing
    # artist record with ID <artist_id> using the new attributes

    return redirect(url_for("show_artist", artist_id=artist_id))


@app.route("/venues/<int:venue_id>/edit", methods=["GET"])
def edit_venue(venue_id):
    form = VenueForm()
    venue = {
        "id": 1,
        "name": "The Musical Hop",
        "genres": ["Jazz", "Reggae", "Swing", "Classical", "Folk"],
        "address": "1015 Folsom Street",
        "city": "San Francisco",
        "state": "CA",
        "phone": "123-123-1234",
        "website": "https://www.themusicalhop.com",
        "facebook_link": "https://www.facebook.com/TheMusicalHop",
        "seeking_talent": True,
        "seeking_description": "We are on the lookout for a local artist to play every two weeks. Please call us.",
        "image_link": "https://images.unsplash.com/photo-1543900694-133f37abaaa5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=400&q=60",
    }
    # TODO: populate form with values from venue with ID <venue_id>
    return render_template("forms/edit_venue.html", form=form, venue=venue)


@app.route("/venues/<int:venue_id>/edit", methods=["POST"])
def edit_venue_submission(venue_id):
    # TODO: take values from the form submitted, and update existing
    # venue record with ID <venue_id> using the new attributes
    return redirect(url_for("show_venue", venue_id=venue_id))


#  Create Artist
@app.route("/artists/create", methods=["GET"])
def create_artist_form():
    form = ArtistForm()
    return render_template("forms/new_artist.html", form=form)


@app.route("/artists/create", methods=["POST"])
def create_artist_submission():
    error = False
    try:
        name = request.form.get("name")
        city = request.form.get("city")
        state = request.form.get("state")
        phone = request.form.get("phone")
        genres = request.form.getlist("genres")
        comma_separated_genres = ",".join(genres)
        image_link = request.form.get("image_link")
        facebook_link = request.form.get("facebook_link")
        website_link = request.form.get("website_link")
        seeking_venue = True if "seeking_venue" in request.form else False
        seeking_description = request.form.get("seeking_description")
        artist = Artist(
            name=name,
            city=city,
            state=state,
            phone=phone,
            genres=comma_separated_genres,
            image_link=image_link,
            facebook_link=facebook_link,
            website_link=website_link,
            seeking_venue=seeking_venue,
            seeking_description=seeking_description,
        )
        db.session.add(artist)
        db.session.commit()
    except:
        error = True
        db.session.rollback()
        print(sys.exc_info())
    finally:
        db.session.close()
    if error:
        flash(
            "An error occurred. Artist "
            + request.form["name"]
            + " could not be listed."
        )
    if not error:
        flash("Artist " + request.form["name"] + " was successfully listed!")
        return render_template("pages/home.html")


# End Create Artist


#  Shows
#  ----------------------------------------------------------------


@app.route("/shows")
def shows():
    shows = Show.query.join(Venue).join(Artist).all()
    data = [
        {
            "venue_id": show.venue_id,
            "venue_name": show.venue.name,
            "artist_id": show.artist_id,
            "artist_name": show.artist.name,
            "artist_image_link": show.artist.image_link,
            "start_time": show.start_time.strftime("%Y-%m-%d %H:%M:%S"),
        }
        for show in shows
    ]
    return render_template("pages/shows.html", shows=data)


# Create Show
@app.route("/shows/create")
def create_shows():
    # renders form. do not touch.
    form = ShowForm()
    return render_template("forms/new_show.html", form=form)


@app.route("/shows/create", methods=["POST"])
def create_show_submission():
    error = False
    try:
        artist_id = request.form["artist_id"]
        venue_id = request.form["venue_id"]
        start_time = request.form["start_time"]
        show = Show(artist_id=artist_id, venue_id=venue_id, start_time=start_time)
        db.session.add(show)
        db.session.commit()
    except:
        error = True
        db.session.rollback()
        print(sys.exc_info())
    finally:
        db.session.close()
    if error:
        flash("An error occured. Show could not be listed.")
    if not error:
        flash("Show was successfully listed.")
    return render_template("pages/home.html")


# End Create Show


@app.errorhandler(404)
def not_found_error(error):
    return render_template("errors/404.html"), 404


@app.errorhandler(500)
def server_error(error):
    return render_template("errors/500.html"), 500


if not app.debug:
    file_handler = FileHandler("error.log")
    file_handler.setFormatter(
        Formatter("%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]")
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info("errors")

# ----------------------------------------------------------------------------#
# Launch.
# ----------------------------------------------------------------------------#

# Default port:
if __name__ == "__main__":
    app.run()

# Or specify port manually:
"""
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
"""
