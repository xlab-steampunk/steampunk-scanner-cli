import sys
from enum import Enum
from pathlib import Path
from typing import List, Optional, Union

import yaml


class SafeLineLoader(yaml.loader.SafeLoader):
    """YAML loader that adds line numbers"""

    def construct_mapping(self, node, deep=False) -> dict:
        """
        Overridden the original construct_mapping method
        :param node: YAML node object
        :param deep: Build objects recursively
        :return: A dict with loaded YAML
        """
        mapping = super(SafeLineLoader, self).construct_mapping(node, deep=deep)
        mapping['__line__'] = node.start_mark.line + 1
        return mapping


class AnsibleEntity(Enum):
    """Enum that can distinct between different Ansible entities"""
    TASK = 1
    PLAYBOOK = 2
    ROLE = 3
    COLLECTION = 4


def _parse_tasks(tasks: List, file_name: str, collections: Optional[List] = None) -> List:
    """
    Parse Ansible tasks and prepare them for scanning
    :param tasks: List of Ansible task dicts
    :param file_name: Name of the original file with tasks
    :param collections: List of Ansible collections for tasks
    :return: List of parsed Ansible tasks that are prepared for scanning
    """
    for task in tasks:
        task.pop("name", None)
        task_line = task.pop("__line__", None)

        # TODO: Remove this spaghetti when API will be able to parse action plugins
        if "action" in task:
            dict_with_module = next((d for d in list(task.values()) if type(d) is dict and "module" in d), None)
            if dict_with_module is not None:
                module_name = dict_with_module.pop("module", None)
                action = task.pop("action", None)
                task[module_name] = action

        for task_key in task:
            if type(task[task_key]) is dict:
                task[task_key].pop("__line__", None)
                task[task_key] = list(task[task_key].keys())
            else:
                task[task_key] = None

        if collections is None:
            collections = []

        task["collections"] = collections
        task["__file__"] = file_name
        task["__line__"] = task_line

    return tasks


def _parse_playbook(playbook: dict, file_name: str) -> List:
    """
    Parse Ansible playbook and prepare it for scanning
    :param playbook: Ansible playbook as dict
    :param file_name: Name of the original file with playbook
    :return: List of parsed Ansible tasks that are prepared for scanning
    """
    playbook.pop("name", None)
    playbook.pop("hosts", None)
    playbook.pop("__line__", None)
    collections = playbook.pop("collections", None)

    return _parse_tasks(playbook.get("tasks", []), file_name, collections)


def _parse_task_file(file: Path) -> List:
    """
    Parse Ansible file
    :param file: Ansible task file
    :return: List of parsed Ansible tasks that are prepared for scanning
    """
    with file.open() as stream:
        return _parse_tasks(yaml.load(stream, Loader=SafeLineLoader), str(file))


def _parse_playbook_file(file: Path) -> List:
    """
    Parse Ansible playbook file
    :param file: Ansible playbook file
    :return: List of parsed Ansible tasks that are prepared for scanning
    """
    with file.open() as stream:
        return _parse_playbook(yaml.load(stream, Loader=SafeLineLoader)[0], str(file.relative_to(Path.cwd())))


def _parse_role_dir(directory: Path) -> List:
    """
    Parse Ansible role
    :param directory: Role directory
    :return: List of parsed Ansible tasks that are prepared for scanning
    """
    parsed_role = []
    for file in (list((directory / "tasks").rglob("*")) + list((directory / "handlers").rglob("*"))):
        if file.is_file():
            with file.open() as stream:
                yaml_dict = yaml.load(stream, Loader=SafeLineLoader)
                parsed_tasks = _parse_tasks(yaml_dict, str(file))
                parsed_role += parsed_tasks
    return parsed_role


def parse_role_dirs(dirs: List[Path]) -> List:
    """
    Parse multiple Ansible roles
    :param dirs: List of roles as directories
    :return: List of parsed Ansible tasks that are prepared for scanning
    """
    parsed_files = []
    for directory in dirs:
        if not directory.is_dir():
            print(f"File {directory.name} is not a valid directory")
            sys.exit(1)
        parsed_files += _parse_role_dir(directory)

    return parsed_files


def _parse_collection_dir(directory: Path) -> List:
    """
    Parse Ansible collection
    :param directory: Collection directory
    :return: List of parsed Ansible tasks that are prepared for scanning
    """
    parsed_collection = []
    for role in (list((directory / "roles").rglob("*"))):
        if role.is_dir():
            parsed_collection += _parse_role_dir(role)
    for playbook in (list((directory / "playbooks").rglob("*"))):
        if playbook.is_file():
            parsed_collection += _parse_playbook_file(playbook)
    return parsed_collection


def parse_ansible_entities(paths: Union[Path, List[Path]], ansible_entity_type: AnsibleEntity) -> List:
    """
    Parse multiple Ansible entities
    :param paths: Path or list of paths to Ansible entities
    :param ansible_entity_type: Type of Ansible files (task files, playbooks, roles or collections)
    :return: List of parsed Ansible tasks that are prepared for scanning
    """
    parsed_ansible_entities = []
    if isinstance(paths, list):
        for path in paths:
            if ansible_entity_type == AnsibleEntity.TASK:
                if not path.is_file():
                    print(f"Task file {path.name} is not a valid file")
                    sys.exit(1)
                parsed_ansible_entities += _parse_task_file(path)
            if ansible_entity_type == AnsibleEntity.PLAYBOOK:
                if not path.is_file():
                    print(f"Playbook {path.name} is not a valid file")
                    sys.exit(1)
                parsed_ansible_entities += _parse_playbook_file(path)
            if ansible_entity_type == AnsibleEntity.ROLE:
                if not path.is_dir():
                    print(f"Role {path.name} is not a valid directory")
                    sys.exit(1)
                parsed_ansible_entities += _parse_role_dir(path)
            if ansible_entity_type == AnsibleEntity.COLLECTION:
                if not path.is_dir():
                    print(f"Collection {path.name} is not a valid directory")
                    sys.exit(1)
                parsed_ansible_entities += _parse_collection_dir(path)

    return parsed_ansible_entities
