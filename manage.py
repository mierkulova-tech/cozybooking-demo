"""Django command-line utility for administrative tasks.

This module serves as the primary entry point for Django management commands
such as running migrations, starting the development server, creating superusers,
and executing custom data seeding scripts.

Typical usage:
    $ python manage.py runserver
    $ python manage.py migrate
"""

import os
import sys


def main() -> None:
    """Run administrative tasks.

    Sets up the default Django settings module and executes commands
    passed via command-line arguments.

    Raises:
        ImportError: If Django cannot be imported or is not installed in the
            current PYTHONPATH/virtual environment.
    """
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == "__main__":
    main()
