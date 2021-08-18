""" Locustfile for load testing IDVA functionality """
import os
import random
import uuid
from locust import HttpUser, task, constant

CLIENT_SECRET = str(os.environ["LOCUST_CLIENT_SECRET"])
CLIENT_ID = str(os.environ["LOCUST_CLIENT_ID"])


class IdemiaUser(HttpUser):
    """Simulate user interaction to the idemia microservice"""

    wait_time = constant(1)
    bearer_token = None

    def on_start(self):
        """Generate the OAuth2.0 token for the user"""
        response = self.client.post(
            "/idemia/oauth2/token",
            data={
                "client_id": CLIENT_ID,
                "client_secret": CLIENT_SECRET,
                "grant_type": "client_credentials",
                "scope": "rpname",
            },
        )
        json_response = response.json()
        self.bearer_token = f"token {json_response['access_token']}"

    @task
    def idemia_locations(self):
        """Perform GET on the Idemia /locations endpoint"""
        zipcode = random.randrange(10000, 99999)
        self.client.get(
            "/idemia/locations/%i" % zipcode,
            name="/locations/zipcode",
            headers={"Authorization": self.bearer_token},
        )

    @task
    def idemia_enrollment(self):
        """Perform create & read operarions on the Idemia /enrollment endpoint"""
        enrollment_uuid = uuid.uuid4()

        # Create
        self.client.post(
            "/idemia/enrollment/",
            data={
                "first_name": "Bob",
                "last_name": "Testington",
                "csp_user_uuid": enrollment_uuid,
            },
            headers={"Authorization": self.bearer_token},
        )

        # Read
        self.client.get(
            "/idemia/enrollment/%s" % enrollment_uuid,
            headers={"Authorization": self.bearer_token},
            name="/idemia/enrollment/uuid",
        )
