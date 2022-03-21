import os
from typing import Optional

import requests

ENDPOINT = os.environ.get("SCANNER_ENDPOINT", "https://scanner.steampunk.si/api")


class Client:
    """A client interface for interacting with Steampunk Scanner API"""

    def __init__(self, url: str, username: Optional[str] = None, password: Optional[str] = None):
        """
        Construct Client object
        :param url: API endpoint url
        :param username: Username for HTTP basic auth
        :param password: Password for HTTP basic auth
        """
        self.url = url.rstrip("/")
        self.username = username
        self.password = password

    def post(self, path: str, payload: object) -> requests.Response:
        """
        Send POST request
        :param path: API endpoint path
        :param payload: Payload object
        :return: Response object
        """
        args = dict(json=payload)
        if self.username:
            args["auth"] = (self.username, self.password)
        return requests.post(f"{self.url}{path}", timeout=10, **args)
