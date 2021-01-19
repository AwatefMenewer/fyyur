#----------Imports---------- #
import os
import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *

#----------App Config---------- #

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)

# TODO: connect to a local postgresql database
migrate = Migrate(app, db)

#----------Models---------- #

class Venue(db.Model):
    __tablename__ = 'Venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))

    # TODO: implement any missing fields, as a database migration using Flask-Migrate
    website = db.Column(db.String(250))
    seeking_talent = db.Column(db.Boolean, default=False)
    seeking_description = db.Column(db.String(120))
    genres = db.Column(db.ARRAY(db.String))
    shows = db.relationship('Show', backref='Venue', lazy=True)

    def __repr__(self):
        return f'<Venue{self.id} name: {self.name} city:{self.city} state:{self.state} address:{self.address} phone:{self.phone}\
         image_link: {self.image_link} facebook_link: {self.facebook_link} website: {self.website}\
         seeking_talent: {self.seeking_talent} seeking_description:{self.seeking_description} genres:{self.genres} >' 

class Artist(db.Model):
    __tablename__ = 'Artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.ARRAY(db.String))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))

    # TODO: implement any missing fields, as a database migration using Flask-Migrate
    seeking_venue = db.Column(db.Boolean, default=False)
    seeking_description = db.Column(db.String(120))
    website = db.Column(db.String(120))
    shows = db.relationship('Show', backref='Artist', lazy=True)

    def __repr__(self):
        return f'<Artist{self.id} name:{self.name} city:{self.city} state:{self.state} phone:{self.phone}\
         genres:{self.genres} image_link{self.image_link}facebook_link:{self.facebook_link}\
         seeking_venue{self.seeking_venue} seeking_description{self.seeking_description} website{self.website} >'
    

# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.
class Show(db.Model):
    __tablename__ = 'Show'

    id = db.Column(db.Integer, primary_key=True)
    venue_id = db.Column(db.Integer, db.ForeignKey(Venue.id), nullable=False)
    artist_id = db.Column(db.Integer, db.ForeignKey(Artist.id), nullable=False)
    start_time = db.Column(db.DateTime, nullable=False,
                           default=datetime.utcnow)

    def __repr__(self):
        return f'<Show:{self.id},Artist:{self.artist_id} Venue:{self.venue_id} start_time{self.start_time}>'

#----------Filters---------- #

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format)

app.jinja_env.filters['datetime'] = format_datetime

#----------Controllers---------- #

@app.route('/')
def index():
  return render_template('pages/home.html')

#----------Venues---------- #
# Get All Venues

@app.route('/venues')
def venues():
    # TODO: replace with real venues data.
    #       num_shows should be aggregated based on number of upcoming shows per venue.
    all_venues = (
        db.session.query(Venue.city, Venue.state)
        .group_by(Venue.city, Venue.state)
        .all()
    )

    data = list()
    for one_venue in all_venues:
        city_and_state = (
            Venue.query.filter(Venue.state == one_venue.state)
            .filter(Venue.city == one_venue.city)
            .all()
        )
        data.append(
            {"city": one_venue.city, "state": one_venue.state, "venues": city_and_state}
        )
    return render_template("pages/venues.html", areas=data)

# Search for Venue

@app.route('/venues/search', methods=['POST'])
def search_venues():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
  search_term = request.form.get("search_term", "")
  result_of_search = Venue.query.filter(Venue.name.ilike(f"%{search_term}%"))
  response = {"count": result_of_search.count(), "data": result_of_search}
  return render_template(
        "pages/search_venues.html", results=response, search_term=search_term
    )

#  Create new Venue 

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
    # TODO: insert form data as a new Venue record in the db, instead
    # TODO: modify data to be the data object returned from db insertion
    form = VenueForm(request.form)
    try:
        new_venue = Venue(
            name=request.form['name'],
            genres=request.form.getlist('genres'),
            address=request.form['address'],
            city=request.form['city'],
            state=request.form['state'],
            phone=request.form['phone'],
            website=request.form['website'],
            facebook_link=request.form['facebook_link'],
            image_link=request.form['image_link'],
            seeking_talent= True  if 'seeking_talent' in request.form else False ,
            seeking_description=request.form['seeking_description']
        )
        db.session.add(new_venue)
        db.session.commit()
        # on successful db insert, flash success
        flash('Venue ' + request.form['name'] + ' was successfully listed!')
    # TODO: on unsuccessful db insert, flash an error instead.
    # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
    # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
    except:
        db.session.rollback()
        flash('An error occurred. Venue ' +
              request.form['name']+ ' could not be listed.')
    finally:
        db.session.close()
    return render_template('pages/home.html')
   
# GET A Venue by id  

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
    # shows the venue page with the given venue_id
    # TODO: replace with real venue data from the venues table, using venue_id
    venues = Venue.query.filter(Venue.id == venue_id).first_or_404()
    all_shows = (
        db.session.query(
            Venue.id.label('venue_id'),
            Artist.id.label('artist_id'),
            Artist.name,
            Artist.image_link,
            Show.start_time,
        )
        .join(Artist, Show.artist_id == Artist.id)
        .join(Venue, Show.venue_id == Venue.id)
        .filter(Venue.id == venue_id)
        .all()
    )

    past_shows = list()
    upcoming_shows = list()
    for show in all_shows:
        data_show = {
            "artist_id": show.artist_id,
            "artist_name": show.name,
            "artist_image_link": show.image_link,
            "start_time": str(show.start_time)
        }
        if show.start_time > datetime.now():
            upcoming_shows.append(data_show)
        else:
            past_shows.append(data_show)
    data = {
        "id": venues.id,
        "name": venues.name,
        "genres": venues.genres,
        "address": venues.address,
        "city": venues.city,
        "state": venues.state,
        "phone": venues.phone,
        "website": venues.website,
        "facebook_link": venues.facebook_link,
        "seeking_talent": venues.seeking_talent,
        "seeking_description": venues.seeking_description,
        "image_link": venues.image_link,
        "past_shows": past_shows,
        "upcoming_shows": upcoming_shows,
        "past_shows_count": len(past_shows),
        "upcoming_shows_count": len(upcoming_shows),
    }  
    return render_template('pages/show_venue.html', venue=data)

# Updata Venue by ID

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
    form = VenueForm()
    # TODO: populate form with values from venue with ID <venue_id>
    venue = Venue.query.get(venue_id)

    form.name.data = venue.name
    form.city.data = venue.city
    form.state.data = venue.state
    form.phone.data = venue.phone
    form.address.data = venue.address
    form.genres.data = venue.genres
    form.facebook_link.data = venue.facebook_link
    form.image_link.data = venue.image_link
    form.website.data = venue.website
    form.seeking_talent.data = venue.seeking_talent
    form.seeking_description.data = venue.seeking_description

    return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # TODO: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes
    form = VenueForm()
    venue = Venue.query.get(venue_id)
    try:
        venue.name=request.form['name']
        venue.genres=request.form.getlist('genres')
        venue.address=request.form['address']
        venue.city=request.form['city']
        venue.state=request.form['state']
        venue.phone=request.form['phone']
        venue.website=request.form['website']
        venue.facebook_link=request.form['facebook_link']
        venue.image_link=request.form['image_link']
        venue.seeking_talent= True  if 'seeking_talent' in request.form else False 
        venue.seeking_description=request.form['seeking_description']
        db.session.commit()
    except: 
        db.session.rollback()
        flash('An error occurred. Venue could not be updated.')
    finally: 
        db.session.close()
        flash('Venue ' + request.form['name']+ 'was successfully updated!')

    return redirect(url_for('show_venue', venue_id=venue_id))

# Delete Venue by ID

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
    # TODO: Complete this endpoint for taking a venue_id, and using
    # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.
    try:
        venue = Venue.query.filter(Venue.id == venue_id).first_or_404()
        db.session.delete(venue)
        db.session.commit()
    except:
        db.session.rollback()
        flash('An error occurred. Venue ')
    finally:
        db.session.close()
    return render_template("pages/venues.html")

  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage

#----------Artists---------- #
#  GET All Artist

@app.route('/artists')
def artists():
    # TODO: replace with real data returned from querying the database
    data = list()
    artists = db.session.query(Artist).all()
    for artist in artists:
        data.append({
            "id": artist.id,
            "name": artist.name
        })
    return render_template('pages/artists.html', artists=data)

# Search for Artist

@app.route('/artists/search', methods=['POST'])
def search_artists():
    # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
    # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
    # search for "band" should return "The Wild Sax Band".
    search_term = request.form.get("search_term", "")
    result_of_search = Artist.query.filter(Artist.name.ilike(f"%{search_term}%"))
    response = {"count": result_of_search.count(), "data": result_of_search}
    return render_template(
        "pages/search_artists.html", results=response, search_term=search_term
    )

#  Create new Artist 

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
    # called upon submitting the new artist listing form
    # TODO: insert form data as a new Venue record in the db, instead
    # TODO: modify data to be the data object returned from db insertion
    form = ArtistForm(request.form)

    try:
        new_artist = Artist(
            name=request.form['name'],
            city=request.form['city'],
            state=request.form['state'],
            phone=request.form['phone'],
            image_link=request.form['image_link'],
            genres=request.form.getlist('genres'),
            facebook_link=request.form['facebook_link'],
            website=request.form['website'],
            seeking_venue= True  if 'seeking_talent' in request.form else False,
            seeking_description= request.form['seeking_description']
        )
        db.session.add(new_artist)
        db.session.commit()
        # on successful db insert, flash success
        flash('Artist ' + request.form['name'] + ' was successfully listed!')
    except:
        db.session.rollback()
        # TODO: on unsuccessful db insert, flash an error instead.
        # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')
        flash('An error occurred. Artist ' +
              data.name + ' could not be listed.')
    finally:
        db.session.close()    
    return render_template('pages/home.html')

# GET A Artist by id  

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
    # shows the venue page with the given artist_id
    # TODO: replace with real venue data from the venues table, using artist_id
    artist = Artist.query.filter(Artist.id == artist_id).first_or_404()
    all_shows = (
        db.session.query(
            Venue.id.label("venue_id"),
            Artist.id.label("artist_id"),
            Artist.name,
            Artist.image_link,
            Show.start_time,
        )
        .join(Artist, Show.artist_id == Artist.id)
        .join(Venue, Venue.id == Show.venue_id)
        .filter(Artist.id == artist_id)
        .all()
    )
    past_shows = list()
    upcoming_shows = list()
    for show in all_shows:
        data_show = {
            "artist_id": show.artist_id,
            "artist_name": show.name,
            "artist_image_link": show.image_link,
            "start_time": str(show.start_time),
        }
        if show.start_time > datetime.now():
            upcoming_shows.append(data_show)
        else:
            past_shows.append(data_show)
    data = {
        "id": artist.id,
        "name": artist.name,
        "genres": artist.genres,
        "city": artist.city,
        "state": artist.state,
        "phone": artist.phone,
        "website": artist.website,
        "facebook_link": artist.facebook_link,
        "seeking_venue": artist.seeking_venue,
        "seeking_description": artist.seeking_description,
        "image_link": artist.image_link,
        "past_shows": past_shows,
        "upcoming_shows": upcoming_shows,
        "past_shows_count": len(past_shows),
        "upcoming_shows_count": len(upcoming_shows),
    }
    return render_template('pages/show_artist.html', artist=data)

# Updata Artist by ID 

@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
    form = ArtistForm()
    # TODO: populate form with fields from artist with ID <artist_id>
    artist = Artist.query.get(artist_id)

    form.name.data = artist.name
    form.city.data = artist.city
    form.state.data = artist.state
    form.phone.data = artist.phone
    form.genres.data = artist.genres
    form.facebook_link.data = artist.facebook_link
    form.image_link.data = artist.image_link
    form.website.data = artist.website
    form.seeking_venue.data = artist.seeking_venue
    form.seeking_description.data = artist.seeking_description

    return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
    # TODO: take values from the form submitted, and update existing
    # artist record with ID <artist_id> using the new attributes
    form = ArtistForm()
    artist = Artist.query.get(artist_id)

    try: 
        artist.name = request.form['name']
        artist.city = request.form['city']
        artist.state = request.form['state']
        artist.phone = request.form['phone']
        artist.genres = request.form.getlist('genres')
        artist.image_link = request.form['image_link']
        artist.facebook_link = request.form['facebook_link']
        artist.website = request.form['website']
        artist.seeking_venue = True  if 'seeking_talent' in request.form else False
        artist.seeking_description = request.form['seeking_description']
        db.session.commit()
    except: 
        db.session.rollback()
        flash('An error occurred. Artist could not be updated.')
    finally: 
        db.session.close()
        flash('Artist ' + request.form['name']+ 'was successfully updated!')

    return redirect(url_for('show_artist', artist_id=artist_id))

# Delete Artist by ID

@app.route('/artists/<artist_id>', methods=['DELETE'])
def delete_artist(artist_id):
    # TODO: Complete this endpoint for taking a artist_id, and using
    # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.
    try:
        artist = Artist.query.filter(Artist.id == artist_id).first_or_404()
        db.session.delete(artist)
        db.session.commit()
    except:
        db.session.rollback()
        flash('An error occurred. Artist ')
    finally:
        db.session.close()
    return render_template("pages/artists.html")

#----------Shows---------- #
#  GET All Shows

@app.route('/shows')
def shows():
    # displays list of shows at /shows
    # TODO: replace with real venues data.
    #       num_shows should be aggregated based on number of upcoming shows per venue.
    data = list()
    shows = db.session.query(Show).all()
    for show in shows:
        venue = Venue.query.filter_by(id=show.venue_id).first_or_404()
        artist = Artist.query.filter_by(id=show.artist_id).first_or_404()
        data.extend([{
            "venue_id": venue.id,
            "venue_name": venue.name,
            "artist_id": artist.id,
            "artist_name": artist.name,
            "artist_image_link": artist.image_link,
            "start_time": str(show.start_time)
        }])

    return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
    # called to create new shows in the db, upon submitting new show listing form
    # TODO: insert form data as a new Show record in the db, instead
    form = ShowForm(request.form)
    try:
        # TODO: insert form data as a new Show record in the db, instead
        new_show = Show(
            artist_id=request.form['artist_id'],
            venue_id=request.form['venue_id'],
            start_time=request.form['start_time'],
        )
        db.session.add(new_show)
        db.session.commit()
        # on successful db insert, flash success
        flash('Show was successfully listed!')
    # TODO: on unsuccessful db insert, flash an error instead.
    # e.g., flash('An error occurred. Show could not be listed.')
    # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
    except:
        db.session.rollback()
        flash('An error occurred. Show could not be listed.')
    finally:
        db.session.close()
    return render_template('pages/home.html')

@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

#----------Launch---------- #

# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
