#!/usr/bin/env python
import os
import sys


def add_pre_commit():
    os.system("cp pre-commit-example .git/hooks/pre-commit")

if __name__ == "__main__":
    add_pre_commit()  # Add pre-commit configurations

    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "hc.settings")

    from django.core.management import execute_from_command_line

    execute_from_command_line(sys.argv)
