from locust import HttpUser, task, between


class DjangoUser(HttpUser):
    wait_time = between(0.1, 0.5)  # Time between user actions

    def on_start(self):
        """Called when a simulated user starts."""
        # Perform login to get the JWT token
        login_response = self.client.post(
            "/auth/login/",  # Replace with your login endpoint
            json={"email": "Jon.Stephens@sakilastaff.com", "password": "1"}  # Replace with valid credentials
        )
        if login_response.status_code == 200:
            # Extract the JWT token from the response
            self.token = login_response.json()['result']['token'].get(
                "access")  # Adjust based on your API response structure
        else:
            raise Exception("Login failed!")

    @task
    def film_actors(self):
        self.client.get("/film/actors/")

    @task
    def films(self):
        self.client.get("/film/films/")

    @task
    def most_popular_actors(self):
        self.client.get("/film/most-popular-actors/")

    @task
    def rent_film(self):
        """Simulate renting a film."""
        headers = {
            "Authorization": f"Bearer {self.token}",  # Include the JWT token in the Authorization header
            "Content-Type": "application/json",
        }
        payload = {
            "customer_id": 621,  # Replace with valid customer ID
            "film_id": 1000       # Replace with valid film ID
        }
        self.client.post("/store-staff-panel/rent-film/", json=payload, headers=headers)
        # if response.status_code != 200:
        #     print(f"Error renting film: {response.text}")
