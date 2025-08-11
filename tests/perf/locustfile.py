from locust import HttpUser, task, between

LIST_MAX_MS = 5000
UPDATE_MAX_MS = 2000


class GudlftUser(HttpUser):
    wait_time = between(0.1, 0.5)

    @task(2)
    def view_login(self):
        with self.client.get("/", name="GET / (index)", catch_response=True) as response:
            if response.elapsed.total_seconds() * 1000 > LIST_MAX_MS:
                response.failure("Index slower than 5s threshold")

    @task(2)
    def view_public_scoreboard(self):
        with self.client.get("/clubs", name="GET /clubs (scoreboard)", catch_response=True) as response:
            if response.elapsed.total_seconds() * 1000 > LIST_MAX_MS:
                response.failure("Scoreboard slower than 5s threshold")

    @task(1)
    def login_and_view_summary(self):
        # Use a known email from seed data
        with self.client.post(
            "/showSummary",
            data={"email": "john@simplylift.co"},
            name="POST /showSummary (login)",
            catch_response=True,
        ) as response:
            if response.elapsed.total_seconds() * 1000 > LIST_MAX_MS:
                response.failure("Login summary slower than 5s threshold")

    @task(1)
    def book_flow(self):
        # Hit booking page then attempt to book 1 place
        with self.client.get(
            "/book/Spring%20Festival/Simply%20Lift",
            name="GET /book/<comp>/<club>",
            catch_response=True,
        ) as response:
            if response.elapsed.total_seconds() * 1000 > LIST_MAX_MS:
                response.failure("Booking page slower than 5s threshold")

        with self.client.post(
            "/purchasePlaces",
            data={
                "competition": "Spring Festival",
                "club": "Simply Lift",
                "places": "1",
            },
            name="POST /purchasePlaces (book)",
            catch_response=True,
        ) as response:
            if response.elapsed.total_seconds() * 1000 > UPDATE_MAX_MS:
                response.failure("Purchase slower than 2s threshold")


