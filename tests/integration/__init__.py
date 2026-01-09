import sys

import pytest


def run():
    sys.exit(pytest.main(["-v", "tests/integration/"]))
