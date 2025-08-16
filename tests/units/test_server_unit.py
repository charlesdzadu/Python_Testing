import pytest
import server


@pytest.fixture()
def client():
    server.app.config.update({
        "TESTING": True,
        "WTF_CSRF_ENABLED": False,
    })
    with server.app.test_client() as client:
        yield client


def test_index_page_renders(client):
    response = client.get("/")
    assert response.status_code == 200
    assert b"GUDLFT Registration" in response.data


def test_unknown_email_redirects_with_flash(client):
    response = client.post("/showSummary", data={"email": "unknown@example.com"}, follow_redirects=True)
    assert response.status_code == 200
    assert b"Unknown email address" in response.data


def test_show_summary_valid_email(client):
    email = server.clubs[0]["email"]
    response = client.post("/showSummary", data={"email": email})
    assert response.status_code == 200
    assert b"Welcome" in response.data


def test_book_page_valid_route(client):
    club = server.clubs[0]["name"]
    # Use the future competition (Summer Championship)
    competition = server.competitions[2]["name"] if len(server.competitions) > 2 else server.competitions[0]["name"]
    response = client.get(f"/book/{competition}/{club}")
    assert response.status_code == 200
    assert competition.encode() in response.data


def test_book_invalid_route_redirects(client):
    response = client.get("/book/Nonexistent/NoClub", follow_redirects=True)
    assert response.status_code == 200
    assert b"GUDLFT Registration" in response.data


def test_purchase_invalid_competition_or_club(client):
    response = client.post("/purchasePlaces", data={
        "competition": "Nonexistent",
        "club": "Nope",
        "places": "1",
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b"Invalid club or competition" in response.data


def test_purchase_invalid_places_value(client):
    club = server.clubs[0]["name"]
    # Use the future competition
    competition = "Summer Championship"
    response = client.post("/purchasePlaces", data={
        "competition": competition,
        "club": club,
        "places": "abc",
    })
    assert b"Invalid number of places" in response.data


def test_purchase_non_positive_places(client):
    club = server.clubs[0]["name"]
    # Use the future competition
    competition = "Summer Championship"
    response = client.post("/purchasePlaces", data={
        "competition": competition,
        "club": club,
        "places": "0",
    })
    assert b"You must request at least 1 place" in response.data


def test_purchase_more_than_twelve_rejected(client):
    club = server.clubs[0]["name"]
    # Use the future competition
    competition = "Summer Championship"
    response = client.post("/purchasePlaces", data={
        "competition": competition,
        "club": club,
        "places": "13",
    })
    assert b"You cannot book more than 12 places" in response.data


def test_purchase_more_than_available_rejected(client, monkeypatch):
    club = server.clubs[0]["name"]
    # Use the future competition
    competition = "Summer Championship"

    # Force low availability for deterministic behavior
    for comp in server.competitions:
        if comp["name"] == competition:
            comp["numberOfPlaces"] = "2"

    response = client.post("/purchasePlaces", data={
        "competition": competition,
        "club": club,
        "places": "3",
    })
    assert b"Not enough places remaining" in response.data


def test_purchase_more_than_points_rejected(client):
    # Pick a club with very few points
    low_points_club = next(c for c in server.clubs if int(c["points"]) <= 4)
    # Use the future competition
    competition = "Summer Championship"
    response = client.post("/purchasePlaces", data={
        "competition": competition,
        "club": low_points_club["name"],
        "places": "5",
    })
    assert b"does not have enough points" in response.data


def test_successful_booking_deducts_points_and_places(client):
    # Work on a fresh competition and club with known values
    club = server.clubs[0]
    # Use the future competition
    competition = next((c for c in server.competitions if c["name"] == "Summer Championship"), server.competitions[0])

    # Save original values
    original_points = int(club["points"])
    original_places = int(competition["numberOfPlaces"])

    # Ensure we can book 1 place
    club["points"] = str(max(1, original_points))
    competition["numberOfPlaces"] = str(max(1, original_places))

    response = client.post("/purchasePlaces", data={
        "competition": competition["name"],
        "club": club["name"],
        "places": "1",
    })
    assert response.status_code == 200
    assert b"booking complete" in response.data.lower()

    assert int(competition["numberOfPlaces"]) == max(1, original_places) - 1
    assert int(club["points"]) == max(1, original_points) - 1


def test_public_scoreboard_accessible(client):
    response = client.get("/clubs")
    assert response.status_code == 200
    assert b"Club Points" in response.data


def test_login_link_to_scoreboard_present(client):
    response = client.get("/")
    assert response.status_code == 200
    assert b"Club Points" in response.data


def test_points_deduction_persists_to_json(client, mock_save_functions):
    """Test that points deduction triggers save functions"""
    mock_save_clubs, mock_save_comps = mock_save_functions
    
    club = server.clubs[0]
    # Use the future competition
    competition = next((c for c in server.competitions if c["name"] == "Summer Championship"), server.competitions[0])
    initial_points = int(club["points"])
    initial_places = int(competition["numberOfPlaces"])
    
    # Make a valid booking
    response = client.post("/purchasePlaces", data={
        "competition": competition["name"],
        "club": club["name"],
        "places": "2",
    })
    assert b"booking complete" in response.data.lower()
    
    # Verify in-memory changes
    assert int(club["points"]) == initial_points - 2
    assert int(competition["numberOfPlaces"]) == initial_places - 2
    
    # Verify save functions were called
    mock_save_clubs.assert_called_once()
    mock_save_comps.assert_called_once()


def test_cannot_book_past_competition(client):
    """Test that booking a past competition is rejected"""
    club = server.clubs[0]["name"]
    # Use a past competition (Spring Festival from 2020)
    past_competition = "Spring Festival"
    
    # Try to access booking page for past competition
    response = client.get(f"/book/{past_competition}/{club}", follow_redirects=False)
    assert response.status_code == 307  # Should redirect
    
    # Try to book directly via POST
    response = client.post("/purchasePlaces", data={
        "competition": past_competition,
        "club": club,
        "places": "1",
    })
    assert b"Cannot book places for past competitions" in response.data
    assert b"(Past competition - booking closed)" in response.data


def test_multiple_bookings_accumulate_deductions(client):
    """Test that multiple bookings properly accumulate point deductions"""
    club = server.clubs[0]
    # Use the future competition
    competition = next((c for c in server.competitions if c["name"] == "Summer Championship"), server.competitions[0])
    
    # Ensure sufficient points and places
    club["points"] = "20"
    competition["numberOfPlaces"] = "20"
    
    initial_points = 20
    
    # First booking
    response = client.post("/purchasePlaces", data={
        "competition": competition["name"],
        "club": club["name"],
        "places": "3",
    })
    assert b"booking complete" in response.data.lower()
    assert int(club["points"]) == initial_points - 3
    
    # Second booking
    response = client.post("/purchasePlaces", data={
        "competition": competition["name"],
        "club": club["name"],
        "places": "2",
    })
    assert b"booking complete" in response.data.lower()
    assert int(club["points"]) == initial_points - 5
    
    # Third booking
    response = client.post("/purchasePlaces", data={
        "competition": competition["name"],
        "club": club["name"],
        "places": "1",
    })
    assert b"booking complete" in response.data.lower()
    assert int(club["points"]) == initial_points - 6


