from functools import cache
from os import PathLike
from pathlib import Path
from subprocess import CalledProcessError, check_output
from typing import Optional

from arf.errors import MissingDependency


@cache
def query_binary_exec(name: str) -> Optional[PathLike]:
    """
    Retrieve the path for a given binary name. If the binary does not exist, None is returned.

    :param name: Name of the binary
    :return: The path to the executable
    """
    try:
        return check_output(["command", "-v", name.strip()])
    except CalledProcessError:
        pass

    return None


def has_binary(name: str) -> bool:
    path = query_binary_exec(name)
    if path and (path := Path(path)):
        return path.exists()

    return False


def get_binary_or_error(name: str) -> Optional[PathLike]:
    if not has_binary(name):
        raise MissingDependency(name)

    return query_binary_exec(name)
