#!/usr/bin/env python
import os
import sys

from hc.settings import DEBUG


def add_pre_commit():
    print('Starting pre-commit setup.....')
    os.system("cp pre-commit-example .git/hooks/pre-commit")
    os.system("chmod +x .git/hooks/pre-commit")
    print("Pre-commit setup complete")

if __name__ == "__main__":
    if DEBUG:
        add_pre_commit()  # Add pre-commit configurations

    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "hc.settings")

    from django.core.management import execute_from_command_line

    execute_from_command_line(sys.argv)
