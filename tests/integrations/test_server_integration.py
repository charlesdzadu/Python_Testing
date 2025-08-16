import pytest
import server


@pytest.fixture()
def client():
    server.app.config.update({
        "TESTING": True,
    })
    with server.app.test_client() as client:
        yield client


def test_full_login_book_logout_flow(client):
    # Login
    email = server.clubs[0]["email"]
    response = client.post("/showSummary", data={"email": email})
    assert response.status_code == 200
    assert b"Welcome" in response.data

    # Use a future competition instead of past one
    comp_name = "Summer Championship"  # This is in 2026
    club_name = server.clubs[0]["name"]
    response = client.get(f"/book/{comp_name}/{club_name}")
    assert response.status_code == 200
    assert comp_name.encode() in response.data

    # Try to book 1 place (if possible)
    comp = next(c for c in server.competitions if c["name"] == comp_name)
    club = next(c for c in server.clubs if c["name"] == club_name)
    comp["numberOfPlaces"] = str(max(1, int(comp["numberOfPlaces"])) )
    club["points"] = str(max(1, int(club["points"])) )

    response = client.post("/purchasePlaces", data={
        "competition": comp_name,
        "club": club_name,
        "places": "1",
    })
    assert response.status_code == 200
    assert b"booking complete" in response.data.lower() or b"great - booking complete" in response.data.lower()

    # Logout
    response = client.get("/logout", follow_redirects=True)
    assert response.status_code == 200
    assert b"GUDLFT Registration" in response.data


def test_points_persist_in_memory_after_booking(client):
    """Integration test: Points deduction persists in memory structures"""
    # Get initial values
    club_name = "Simply Lift"
    comp_name = "Summer Championship"  # Use future competition
    club = next(c for c in server.clubs if c["name"] == club_name)
    competition = next(c for c in server.competitions if c["name"] == comp_name)
    initial_points = int(club["points"])
    initial_places = int(competition["numberOfPlaces"])
    
    # Make a booking
    response = client.post("/purchasePlaces", data={
        "competition": comp_name,
        "club": club_name,
        "places": "3",
    })
    assert b"booking complete" in response.data.lower() or b"great - booking complete" in response.data.lower()
    
    # Check that points are deducted in the server's memory
    assert int(club["points"]) == initial_points - 3
    assert int(competition["numberOfPlaces"]) == initial_places - 3
    
    # Verify the changes are reflected in subsequent requests
    response = client.get("/clubs")
    assert str(initial_points - 3).encode() in response.data


def test_concurrent_bookings_maintain_consistency(client):
    """Test that multiple bookings from different clubs maintain data consistency"""
    club1 = server.clubs[0]
    club2 = server.clubs[1]
    # Use future competition (Summer Championship is at index 2)
    competition = server.competitions[2]
    
    # Set up initial state
    club1["points"] = "10"
    club2["points"] = "10"
    competition["numberOfPlaces"] = "10"
    
    initial_places = 10
    
    # First club books
    response = client.post("/purchasePlaces", data={
        "competition": competition["name"],
        "club": club1["name"],
        "places": "3",
    })
    assert b"booking complete" in response.data.lower() or b"great - booking complete" in response.data.lower()
    assert int(competition["numberOfPlaces"]) == initial_places - 3
    assert int(club1["points"]) == 7
    
    # Second club books
    response = client.post("/purchasePlaces", data={
        "competition": competition["name"],
        "club": club2["name"],
        "places": "2",
    })
    assert b"booking complete" in response.data.lower() or b"great - booking complete" in response.data.lower()
    assert int(competition["numberOfPlaces"]) == initial_places - 5
    assert int(club2["points"]) == 8
    assert int(club1["points"]) == 7  # First club's points unchanged


def test_booking_updates_reflected_in_scoreboard(client):
    """Test that point deductions are immediately visible in the scoreboard"""
    club = server.clubs[0]
    # Use future competition (Summer Championship is at index 2)
    competition = server.competitions[2]
    
    # Set known initial state
    club["points"] = "15"
    competition["numberOfPlaces"] = "10"
    club_name = club["name"]
    
    # Check initial scoreboard
    response = client.get("/clubs")
    assert response.status_code == 200
    assert b"15" in response.data
    
    # Make a booking
    response = client.post("/purchasePlaces", data={
        "competition": competition["name"],
        "club": club_name,
        "places": "5",
    })
    assert b"booking complete" in response.data.lower() or b"great - booking complete" in response.data.lower()
    
    # Check updated scoreboard
    response = client.get("/clubs")
    assert response.status_code == 200
    # Club should now have 10 points (15 - 5)
    assert b"10" in response.data


