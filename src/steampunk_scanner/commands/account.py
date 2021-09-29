import argparse
from getpass import getpass

from steampunk_scanner import api


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
    password = getpass()
    client = api.Client(api.ENDPOINT)
    response = client.post(
        "/accounts/register", dict(username=args.username, password=password)
    )
    if response.ok:
        print(response.json()["msg"])
    else:
        print(f"API error: {response.status_code} - {response.json()['msg']}")
        exit(1)


def _parser_callback_activate(args: argparse.Namespace):
    """
    Activates pending account
    :param args: Argparse arguments
    """
    client = api.Client(api.ENDPOINT)
    response = client.post(
        "/accounts/activate",
        dict(username=args.username, verification_code=args.verification_code)
    )
    if response.ok:
        print(response.json()["msg"])
    else:
        print(f"API error: {response.status_code} - {response.json()['msg']}")
        exit(1)
