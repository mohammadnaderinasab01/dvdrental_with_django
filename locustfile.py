from locust import HttpUser, task, between


class DjangoUser(HttpUser):
    wait_time = between(0.1, 0.5)  # Time between user actions

    @task
    def homepage(self):
        self.client.get("/film/actors/")

    @task(3)
    def some_api(self):
        self.client.get("/film/films/")
