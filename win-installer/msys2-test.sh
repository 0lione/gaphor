#!/bin/bash

set -e

export PYTEST_ADDOPTS="--doctest-modules --junitxml=junit/test-results.xml"
export PY_IGNORE_IMPORTMISMATCH=1

source venv
python3 -m pytest
