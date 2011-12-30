#!/usr/bin/env python
# coding=utf-8
import os
import os.path
import subprocess
import sys


# The root directory of the project and the project's name.
ROOT = os.path.dirname(os.path.abspath(__file__))
NAME = os.path.basename(ROOT)


# Output colours. We need to define these ourselves because we don't want to
# make any assumptions about what's available on the system.
def _wrap_colour(code):
    """Returns a function that wraps text in the given ANSI escape code."""
    def inner(text):
       return "\033[1;%sm%s\033[0m" % (code, text)

    return inner


red = _wrap_colour("31")
green = _wrap_colour("32")


def check_call(arguments):
    """A silent version of subprocess's ``check_call()``."""
    try:
        devnull = open(os.devnull, "w")
        subprocess.check_call(arguments, stderr=devnull, stdout=devnull)
    finally:
        devnull.close()


def create_virtualenv():
    """Creates the project's virtualenv directory."""
    print "> Creating a virtualenv..."

    try:
        check_call(["virtualenv", "--no-site-packages", get_virtualenv_path()])
    except subprocess.CalledProcessError:
        print >> sys.stderr, red("Couldn't create a virtualenv.")
        sys.exit(1)


def executable_exists(executable):
    """Check if an executable exists on the path.

    .. code-block:: python

        >>> executable_exists("python")
        True
        >>> executable_exists("not_python")
        False

    :param executable: The name of the executable to check for.
    :type  executable: ``str``
    :returns: ``True`` if the executable is on the path; ``False`` otherwise.
    :rtype: ``bool``
    """
    try:
        # If no executables could be found, which's returned code will be 1,
        # causing a subprocess.CalledProcessError exception to be raised.
        check_call(["which", executable])
        return True
    except subprocess.CalledProcessError:
        return False


def get_virtualenv_path():
    """Returns the path to the project's virtualenv."""
    return os.path.join(ROOT, "environment")


def install_requirements():
    """Installs the project's requirements to the virtualenv."""
    print "> Installing requirements..."

    # Do we have a local cache?
    if os.path.exists(os.path.join(ROOT, "requirements_cache")):
        print "Some requirements are cached locally; we'll use those."

    try:
        # Install the packages listed in requirements.txt into the project's
        # virtualenv, opting to use those in the local cache if available.
        check_call(["pip", "install", "--download-cache", "requirements_cache",
                    "-E", get_virtualenv_path(), "-r", "requirements.txt"])
    except subprocess.CalledProcessError:
        print >> sys.stderr, red("Couldn't install the requirements.")
        sys.exit(1)


def main():
    """The main bootstrap function."""
    if not executable_exists("virtualenv"):
        print >> sys.stderr, red("virtualenv must be installed.")
        sys.exit(1)

    if not executable_exists("pip"):
        print >> sys.stderr, red("pip must be installed.")
        sys.exit(1)

    create_virtualenv()
    install_requirements()

    print green("Done! Now just run `source environment/bin/activate`.")


if __name__ == "__main__":
    main()
