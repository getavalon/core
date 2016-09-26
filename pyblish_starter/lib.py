import os
import re
import errno
import datetime


def listdir(dirname):
    """Prefer empty list to OSError on os.listdir

    Example:
        >>> listdir("/definitely/does/not/exist")
        []
        >>> listdir(os.path.expanduser("~")) != []
        True

    """

    try:
        return os.listdir(dirname)
    except OSError as e:
        # Only handle missing directories
        if e.errno == errno.ENOENT:  # No such file or directory
            return list()
        raise


def time():
    """Return file-system safe string of current date and time"""
    return datetime.datetime.now().strftime("%Y%m%dT%H%M%SZ")


def format_shared_dir(root):
    return os.path.join(root, "shared")


def format_staging_dir(root, name):
    dirname = os.path.join(root, "stage", time(), name)
    return dirname


def parse_version(version):
    """Return integer version from formatted string

    Returns:
        integer version number

    Raises:
        ValueError when integer could not be found

    Example:
        >>> parse_version("v001")
        1
        >>> parse_version("2")
        2
        >>> parse_version("version03")
        3
        >>> parse_version("000008")
        8
        >>> parse_version("abc")
        Traceback (most recent call last):
        ...
        ValueError: Could not parse "abc"

    """

    matches = re.findall(r"\d+", version)

    if not matches:
        raise ValueError("Could not parse \"%s\"" % version)

    return int(matches[-1])


def format_version(version):
    """Produce filesystem-friendly string from integer version

    Arguments:
        version (int): Version number

    Returns:
        string of `version`.

    Raises:
        TypeError on non-integer version

    Example:
        >>> format_version(5)
        'v005'
        >>> format_version("x")
        Traceback (most recent call last):
        ...
        TypeError: %d format: a number is required, not str

    """

    return "v%03d" % version


def find_latest_version(versions):
    """Return latest version from list of versions

    If multiple numbers are found in a single version,
    the last one found is used. E.g. (6) from "v7_22_6"

    Arguments:
        versions (list): Version numbers as string

    Example:
        >>> find_latest_version(["v001", "v002", "v003"])
        3
        >>> find_latest_version(["1", "2", "3"])
        3
        >>> find_latest_version(["v1", "v0002", "verision_3"])
        3
        >>> find_latest_version(["v2", "5_version", "verision_8"])
        8
        >>> find_latest_version(["v2", "v3_5", "_1_2_3", "7, 4"])
        5
        >>> find_latest_version(["v010", "v011"])
        11

    """

    highest_version = 0
    for version in versions:
        version = parse_version(version)

        if version > highest_version:
            highest_version = version

    return highest_version
