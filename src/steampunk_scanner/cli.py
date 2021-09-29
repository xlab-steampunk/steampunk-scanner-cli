import argparse
import inspect
import sys

from steampunk_scanner import commands


class ArgParser(argparse.ArgumentParser):
    """An argument parser that displays help on error"""

    def error(self, message):
        """
        Overridden the original error method
        :param message: Error message
        """
        sys.stderr.write("error: {}\n".format(message))
        self.print_help()
        sys.exit(2)

    def add_subparsers(self, **kwargs):
        """
        Overridden the original add_subparsers method (workaround for http://bugs.python.org/issue9253)
        """
        subparsers = super(ArgParser, self).add_subparsers()
        subparsers.required = True
        subparsers.dest = "command"
        return subparsers


def create_parser():
    """
    Create argument parser for CLI
    :return: Parser as argparse.ArgumentParser object
    """
    parser = ArgParser(description="Steampunk Scanner - a quality scanner for Ansible Playbooks")

    subparsers = parser.add_subparsers()
    cmds = inspect.getmembers(commands, inspect.ismodule)
    for _, module in sorted(cmds, key=lambda x: x[0]):
        module.add_parser(subparsers)
    return parser


def main():
    """
    Main CLI method to be called
    """
    parser = create_parser()
    args = parser.parse_args()
    return args.func(args)
