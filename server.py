import json
from datetime import datetime
from flask import Flask,render_template,request,redirect,flash,url_for


def loadClubs():
    with open('clubs.json') as c:
         listOfClubs = json.load(c)['clubs']
         return listOfClubs


def loadCompetitions():
    with open('competitions.json') as comps:
         listOfCompetitions = json.load(comps)['competitions']
         return listOfCompetitions


def saveClubs(clubs_list):
    with open('clubs.json', 'w') as c:
        json.dump({'clubs': clubs_list}, c, indent=4)


def saveCompetitions(competitions_list):
    with open('competitions.json', 'w') as comps:
        json.dump({'competitions': competitions_list}, comps, indent=4)


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
    
    # Add is_past flag to each competition
    current_time = datetime.now()
    competitions_with_status = []
    for comp in competitions:
        comp_copy = comp.copy()
        comp_date = datetime.strptime(comp['date'], '%Y-%m-%d %H:%M:%S')
        comp_copy['is_past'] = comp_date < current_time
        competitions_with_status.append(comp_copy)
    
    return render_template('welcome.html', club=club, competitions=competitions_with_status)


@app.route('/book/<competition>/<club>')
def book(competition,club):
    foundClub = next((c for c in clubs if c['name'] == club), None)
    foundCompetition = next((c for c in competitions if c['name'] == competition), None)
    
    if not foundClub or not foundCompetition:
        flash("Something went wrong-please try again")
        return redirect(url_for('index'))
    
    # Check if competition date is in the past
    competition_date = datetime.strptime(foundCompetition['date'], '%Y-%m-%d %H:%M:%S')
    if competition_date < datetime.now():
        flash("Cannot book places for past competitions")
        return redirect(url_for('showSummary'), code=307)
    
    return render_template('booking.html', club=foundClub, competition=foundCompetition)


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
    
    # Check if competition date is in the past
    competition_date = datetime.strptime(competition['date'], '%Y-%m-%d %H:%M:%S')
    current_time = datetime.now()
    if competition_date < current_time:
        flash("Cannot book places for past competitions")
        # Add is_past flag to each competition
        competitions_with_status = []
        for comp in competitions:
            comp_copy = comp.copy()
            comp_date = datetime.strptime(comp['date'], '%Y-%m-%d %H:%M:%S')
            comp_copy['is_past'] = comp_date < current_time
            competitions_with_status.append(comp_copy)
        return render_template('welcome.html', club=club, competitions=competitions_with_status)

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

    competition['numberOfPlaces'] = str(available_places - placesRequired)
    club['points'] = str(club_points - placesRequired)
    
    saveClubs(clubs)
    saveCompetitions(competitions)

    flash(f'Great - booking complete! You booked {placesRequired} place(s).')
    
    # Add is_past flag to each competition
    current_time = datetime.now()
    competitions_with_status = []
    for comp in competitions:
        comp_copy = comp.copy()
        comp_date = datetime.strptime(comp['date'], '%Y-%m-%d %H:%M:%S')
        comp_copy['is_past'] = comp_date < current_time
        competitions_with_status.append(comp_copy)
    
    return render_template('welcome.html', club=club, competitions=competitions_with_status)


@app.route('/clubs')
def displayClubsPoints():
    # Public read-only table of club points
    sorted_clubs = sorted(clubs, key=lambda c: int(c['points']), reverse=True)
    return render_template('scoreboard.html', clubs=sorted_clubs)


@app.route('/logout')
def logout():
    return redirect(url_for('index'))