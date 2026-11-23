import pytest

from raffle_edge.db.database import connect


@pytest.fixture
def conn():
    c = connect(":memory:")
    yield c
    c.close()
