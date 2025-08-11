import json
from flask import Flask,render_template,request,redirect,flash,url_for


def loadClubs():
    with open('clubs.json') as c:
         listOfClubs = json.load(c)['clubs']
         return listOfClubs


def loadCompetitions():
    with open('competitions.json') as comps:
         listOfCompetitions = json.load(comps)['competitions']
         return listOfCompetitions


app = Flask(__name__)
app.secret_key = 'something_special'

competitions = loadCompetitions()
clubs = loadClubs()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/showSummary',methods=['POST'])
def showSummary():
    email = request.form.get('email', '').strip()
    club = next((club for club in clubs if club['email'] == email), None)
    if not club:
        flash('Unknown email address. Please try again.')
        return redirect(url_for('index'))
    return render_template('welcome.html', club=club, competitions=competitions)


@app.route('/book/<competition>/<club>')
def book(competition,club):
    foundClub = next((c for c in clubs if c['name'] == club), None)
    foundCompetition = next((c for c in competitions if c['name'] == competition), None)
    if foundClub and foundCompetition:
        return render_template('booking.html', club=foundClub, competition=foundCompetition)
    flash("Something went wrong-please try again")
    return redirect(url_for('index'))


@app.route('/purchasePlaces',methods=['POST'])
def purchasePlaces():
    competition_name = request.form.get('competition', '').strip()
    club_name = request.form.get('club', '').strip()
    places_raw = request.form.get('places', '').strip()

    competition = next((c for c in competitions if c['name'] == competition_name), None)
    club = next((c for c in clubs if c['name'] == club_name), None)

    if not competition or not club:
        flash('Invalid club or competition.')
        return redirect(url_for('index'))

    try:
        placesRequired = int(places_raw)
    except ValueError:
        flash('Invalid number of places.')
        return render_template('booking.html', club=club, competition=competition)

    if placesRequired <= 0:
        flash('You must request at least 1 place.')
        return render_template('booking.html', club=club, competition=competition)

    available_places = int(competition['numberOfPlaces'])
    club_points = int(club['points'])

    if placesRequired > 12:
        flash('You cannot book more than 12 places for a single competition.')
        return render_template('booking.html', club=club, competition=competition)

    if placesRequired > available_places:
        flash('Not enough places remaining in this competition.')
        return render_template('booking.html', club=club, competition=competition)

    if placesRequired > club_points:
        flash('Your club does not have enough points to complete this booking.')
        return render_template('booking.html', club=club, competition=competition)

    competition['numberOfPlaces'] = available_places - placesRequired
    club['points'] = club_points - placesRequired

    flash(f'Great - booking complete! You booked {placesRequired} place(s).')
    return render_template('welcome.html', club=club, competitions=competitions)


@app.route('/clubs')
def displayClubsPoints():
    # Public read-only table of club points
    sorted_clubs = sorted(clubs, key=lambda c: int(c['points']), reverse=True)
    return render_template('scoreboard.html', clubs=sorted_clubs)


@app.route('/logout')
def logout():
    return redirect(url_for('index'))