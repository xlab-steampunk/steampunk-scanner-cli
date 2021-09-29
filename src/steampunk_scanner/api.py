import requests

# TODO: Change this development API endpoint to a real one when production API auth works and when this CLI is ready
ENDPOINT = "http://10.44.17.54/api"


class Client:
    def __init__(self, url, username=None, password=None):
        self.url = url.rstrip("/")
        self.username = username
        self.password = password

    def post(self, path, payload):
        args = dict(json=payload)
        if self.username:
            args["auth"] = (self.username, self.password)
        return requests.post(f"{self.url}{path}", **args)
