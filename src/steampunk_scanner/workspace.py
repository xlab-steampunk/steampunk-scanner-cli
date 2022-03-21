import json
import platform
import subprocess
from typing import NamedTuple, Optional

import pkg_resources


class Workspace:
    """User workspace state discovery (retrieves system info and versions of installed packages)"""

    def __init__(self):
        """Construct Workspace object"""
        self.platform = None
        self.python_version = None
        self.ansible_python_version = None
        self.ansible_core_python_version = None
        self.ansible_version = None
        self.ansible_collections = None

    def discover(self):
        """Set discovered workspace variables"""
        self.platform = self._get_platform()
        self.python_version = self._get_python_version()
        self.ansible_python_version = self._get_ansible_python_version()
        self.ansible_core_python_version = self._get_ansible_core_python_version()
        self.ansible_version = self._get_ansible_version()
        self.ansible_collections = self._get_ansible_collections()

    def _get_platform(self) -> NamedTuple:
        """
        Get OS platform info
        :return: NamedTuple
        """
        return platform.uname()

    def _get_python_version(self) -> str:
        """
        Get python version
        :return: Version string
        """
        return platform.python_version()

    def _get_ansible_python_version(self) -> Optional[str]:
        """
        Get ansible python package version
        :return: Version string
        """
        try:
            return pkg_resources.get_distribution("ansible").version
        except pkg_resources.DistributionNotFound:
            return None

    def _get_ansible_core_python_version(self) -> Optional[str]:
        """
        Get ansible-core python package version
        :return: Version string
        """
        try:
            return pkg_resources.get_distribution("ansible-core").version
        except pkg_resources.DistributionNotFound:
            return None

    def _get_ansible_version(self) -> Optional[str]:
        """
        Get Ansible version
        :return: Version string
        """
        try:
            output = subprocess.check_output(["ansible", "--version"]).decode('utf-8')
            return output.splitlines()[0].lower().replace('ansible', '').strip()
        except subprocess.CalledProcessError:
            return None

    def _get_ansible_collections(self) -> Optional[dict]:
        """
        Get installed Ansible collections
        :return: Dict with Ansible collection names and their versions
        """
        try:
            output = subprocess.check_output(["ansible-galaxy", "collection", "list", "--format", "json"]).decode(
                'utf-8')
            return json.loads(output)
        except subprocess.CalledProcessError:
            return None
