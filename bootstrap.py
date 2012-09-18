#!/usr/bin/env python
# coding=utf-8
import os
import os.path
from subprocess import CalledProcessError, check_call, check_output, STDOUT
import sys


# The root directory of the project and the project's name.
ROOT = os.path.dirname(os.path.abspath(__file__))
NAME = os.path.basename(ROOT)
VIRTUALENV_PATH = os.path.join(ROOT, ".env")


# Output colours. We need to define these ourselves because we don't want to
# make any assumptions about what's available on the system.
def _wrap_colour(code):
    """Returns a function that wraps text in the given ANSI escape code."""
    def inner(text):
        return "\033[1;%sm%s\033[0m" % (code, text)

    return inner


red = _wrap_colour("31")
green = _wrap_colour("32")


def silent_call(arguments):
    """A silent version of subprocess's ``check_call()``."""
    try:
        devnull = open(os.devnull, "w")
        check_call(arguments, stderr=devnull, stdout=devnull)
    finally:
        devnull.close()


def create_virtualenv():
    """Creates the project's virtualenv directory."""
    print "> Creating a virtualenv..."

    try:
        silent_call(["virtualenv", "--no-site-packages", VIRTUALENV_PATH])
    except CalledProcessError:
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
        silent_call(["which", executable])
        return True
    except CalledProcessError:
        return False


def investigate_and_report(error):
    """Print a message explaining the exception.

    :type error: CalledProcessError object with ``output`` attribute
    """
    guesses = {"libmemcached": "'libmemcached/memcached.h' file not found"}
    for libary, signature in guesses.items():
        if signature in error.output:
            reason = "'%s' is required but not installed." % libary
            print >> sys.stderr, red(reason)


def install_requirements():
    """Installs the project's requirements to the virtualenv."""
    print "> Installing requirements..."

    try:
        # Install the packages listed in requirements.txt into the project's
        # virtualenv, opting to use those in the local cache if available.
        pip = os.path.join(VIRTUALENV_PATH, "bin", "pip")
        check_output([pip, "install", "-r", "requirements.txt"], stderr=STDOUT)
    except CalledProcessError as e:
        investigate_and_report(e)
        sys.exit(1)


def main():
    """The main bootstrap function."""
    if not executable_exists("virtualenv"):
        print >> sys.stderr, red("virtualenv must be installed.")
        sys.exit(1)

    if not executable_exists("pip"):
        print >> sys.stderr, red("pip must be installed.")
        sys.exit(1)

    # Honor PIP_DOWNLOAD_CACHE environment variable.
    os.environ.setdefault("PIP_DOWNLOAD_CACHE",
                          os.path.join(ROOT, "requirements_cache"))

    create_virtualenv()
    install_requirements()

    print green("Done! Now just run `. .env/bin/activate`.")


if __name__ == "__main__":
    main()
