import pytest
from aero_ai.schemas import Requirements
from aero_ai.templates.fixed_wing.sizing import size_fixed_wing
from aero_ai.templates.fixed_wing.balance import balance_fixed_wing
from aero_ai.templates.fixed_wing.trim import trim_fixed_wing


@pytest.fixture(scope="session")
def req():
    return Requirements("fixed_wing", payload_kg=1.0, endurance_min=45, cruise_speed_ms=15)


@pytest.fixture(scope="session")
def sized(req):
    return size_fixed_wing(req)


@pytest.fixture(scope="session")
def balanced(sized, req):
    return balance_fixed_wing(sized, req)      # solved once, shared by all tests


@pytest.fixture(scope="session")
def trimmed(balanced, req):
    return trim_fixed_wing(balanced, req)      # solved once, shared by all tests
