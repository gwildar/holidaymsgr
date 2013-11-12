#!/usr/bin/env python
import os
import sys

import wingdbstub

def main():
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "holidaymsgr.settings")
    from django.core.management import execute_from_command_line
    execute_from_command_line(sys.argv)