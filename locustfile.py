from locust import HttpUser, TaskSet, task, between
import random

class UserActions(HttpUser):
    wait_time = between(1, 2)


    # def on_start(self):
    #     self.client.post("/login/", {"username": "admin", "password": "admin"})

    @task
    def home(self):
        self.client.get("/")
    

    # @task 
    # def add_file(self):
    #     data = {
    #         'group': random.randint(1, 3),
    #     }
    #     files = {'file': ('example.txt', b'File content')}
    #     self.client.post('/add-file/', data=data, files=files, catch_response=True)
        # response = self.client.get("/home/")
        # if response.status_code != 200:
        #     response.failure("Home page not loaded after file upload")

    # @task
    # def add_group(self):
    #     self.client.get('/add-group/')

    # @task
    # def all_groups(self):
    #     self.client.get('/all-groups/')

    # @task
    # def checkin(self):
    #     file_id = random.randint(1, 4)
    #     self.client.get(f'/checkin/{file_id}')

    # @task
    # def check_file_status(self):
    #     file_id = random.randint(1, 4)
    #     self.client.get(f'/check-file-status/{file_id}')

    # @task
    # def group_checkin(self):
    #     group_id = random.randint(1, 2)
    #     self.client.get(f'/group-checkin/{group_id}')

    # @task
    # def download_file(self):
    #     file_id = random.randint(1, 4)
    #     self.client.get(f'/download-file/{file_id}')

    # @task
    # def generate_report(self):
    #     file_id = random.randint(1, 4)
    #     self.client.get(f'/generate-report/{file_id}')

    # @task
    # def delete_file(self):
    #     file_id = random.randint(1, 4)
    #     self.client.get(f'/delete-file/{file_id}')

    # @task
    # def delete_group(self):
    #     group_id = random.randint(1, 2)
    #     self.client.get(f'/delete-group/{group_id}')

    # @task
    # def logout(self):
    #     self.client.get('/logout/')