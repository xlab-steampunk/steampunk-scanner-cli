import argparse
import json
from getpass import getpass

import requests

from src.cli import API_ENDPOINT


def add_parser(subparsers):
    parser = subparsers.add_parser(
        "account", help="Manage user account", description="Manage user account"
    )

    subsubparsers = parser.add_subparsers()
    parser_new = subsubparsers.add_parser(
        "register", help="Register a new account", description="Register a new account"
    )
    parser_new.add_argument(
        "username", type=str, help="User email"
    )
    parser_new.set_defaults(func=_parser_callback_new)

    parser_activate = subsubparsers.add_parser(
        "activate", help="Activate pending account", description="Activate pending account"
    )
    parser_activate.add_argument(
        "username", type=str, help="User email"
    )
    parser_activate.add_argument(
        "verification_code", type=str, help="User account verification code from email"
    )
    parser_activate.set_defaults(func=_parser_callback_activate)


def _parser_callback_new(args: argparse.Namespace):
    """
    Registers a new account
    :param args: Argparse arguments
    """
    try:
        password = getpass()
        response = requests.post(f"{API_ENDPOINT}/accounts/register",
                                 data={"username": args.username, "password": password})
        if response.ok:
            json_output = json.loads(response.text)
            print(json_output.get("msg", None))
        else:
            print(f"API error: {response.status_code} - {response.reason}")
            exit(1)
    except Exception as e:
        print(e)
        exit(1)


def _parser_callback_activate(args: argparse.Namespace):
    """
    Activates pending account
    :param args: Argparse arguments
    """
    try:
        password = getpass()
        response = requests.post(f"{API_ENDPOINT}/accounts/activate",
                                 data={"username": args.username, "verification_code": password})
        if response.ok:
            json_output = json.loads(response.text)
            print(json_output.get("msg", None))
        else:
            print(f"API error: {response.status_code} - {response.reason}")
            exit(1)
    except Exception as e:
        print(e)
        exit(1)
