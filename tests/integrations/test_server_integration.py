import json
import pytest
import server


@pytest.fixture(autouse=True)
def reset_data():
    with open('clubs.json') as c:
        server.clubs = json.load(c)['clubs']
    with open('competitions.json') as comps:
        server.competitions = json.load(comps)['competitions']


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

    # Go to booking page
    comp_name = server.competitions[0]["name"]
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
    assert b"booking complete" in response.data.lower()

    # Logout
    response = client.get("/logout", follow_redirects=True)
    assert response.status_code == 200
    assert b"GUDLFT Registration" in response.data


