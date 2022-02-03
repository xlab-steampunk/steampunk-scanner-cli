import requests
import os

ENDPOINT = os.environ.get("SCANNER_ENDPOINT", "https://scanner.steampunk.si/api")


class Client:
    def __init__(self, url, username=None, password=None):
        self.url = url.rstrip("/")
        self.username = username
        self.password = password

    def post(self, path, payload):
        args = dict(json=payload)
        if self.username:
            args["auth"] = (self.username, self.password)
        return requests.post(f"{self.url}{path}", timeout=10, **args)
