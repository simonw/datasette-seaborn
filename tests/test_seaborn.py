from datasette.app import Datasette
import httpx
import pathlib
import pytest
import sqlite3


@pytest.fixture(scope="session")
def ds(tmp_path_factory):
    db_directory = tmp_path_factory.mktemp("dbs")
    db_path = str(db_directory / "penguins.db")
    conn = sqlite3.connect(db_path)
    conn.executescript((pathlib.Path(__file__).parent / "penguins.sql").read_text())
    ds = Datasette([db_path])
    return ds


@pytest.mark.asyncio
async def test_basic_plot(ds):
    app = ds.app()
    async with httpx.AsyncClient(app=app) as client:
        response = await client.get("http://localhost/penguins/penguins.seaborn")
        assert response.status_code == 500
        assert response.text == "_seaborn= is required"
        # Now try with _seaborn=relplot
        response = await client.get(
            "http://localhost/penguins/penguins.seaborn?_seaborn=relplot"
        )
        assert response.status_code == 200
        assert response.headers["content-type"] == "image/png"
