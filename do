#!/bin/bash
# Use this script as a shortcut for invoking verbose commands
# Example Usage: `./do test_prep`

case $1 in
    # Install unit test dependencies
    test_prep ) pip install -r tests/requirements.txt ;;

    # Run unit tests
    test ) python3 tests/manage.py test tests -v 2 ;;
esac