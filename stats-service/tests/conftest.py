import os
import sys
import tempfile

import pytest

_tmpdir = tempfile.mkdtemp()
os.environ["STATS_DB_PATH"] = f"sqlite:///{_tmpdir}/test_stats.db"

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


@pytest.fixture
def client():
    from fastapi.testclient import TestClient
    import main

    Base = main.Base
    Base.metadata.drop_all(main.engine)
    Base.metadata.create_all(main.engine)

    with TestClient(main.app) as c:
        yield c
