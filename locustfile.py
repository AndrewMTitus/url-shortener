from locust import HttpUser, TaskSet, task, between

class UserBehavior(TaskSet):
    @task
    def create_url(self):
        self.client.post("/create_url", json={
            "url": "https://example.com",
            "custom_alias": "testalias"
        }, headers={
            "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbiIsImV4cCI6MTcyNjM0OTgzMn0.CtQeYB1rFPpPS5mR2Zof5bUGb5yPk9aoB3ki232ESls

        })

class WebsiteUser(HttpUser):
    tasks = [UserBehavior]
    wait_time = between(1, 5)

