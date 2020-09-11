from datasette.app import Datasette
import httpx
import pathlib
import pytest
import struct
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
async def test_requires_seaborn(ds):
    app = ds.app()
    async with httpx.AsyncClient(app=app) as client:
        response = await client.get("http://localhost/penguins/penguins.seaborn")
        assert response.status_code == 500
        assert response.text == "_seaborn= is required"


@pytest.mark.asyncio
async def test_image_dimensions_do_not_leak(ds):
    # https://github.com/simonw/datasette-seaborn/issues/1#issuecomment-691187197
    app = ds.app()

    async def get_dims(path):
        async with httpx.AsyncClient(app=app) as client:
            response = await client.get("http://localhost{}".format(path))
            assert response.status_code == 200
            assert response.headers["content-type"] == "image/png"
            return png_dims(response.content)

    histplot_dims = await get_dims("/penguins/penguins.seaborn?_seaborn=histplot")

    relplot_dims = await get_dims("/penguins/penguins.seaborn?_seaborn=relplot")

    dims3 = await get_dims("/penguins/penguins.seaborn?_seaborn=histplot")
    assert dims3 == histplot_dims

    dims4 = await get_dims("/penguins/penguins.seaborn?_seaborn=relplot")
    assert dims4 == relplot_dims


def png_dims(png_bytes):
    w, h = struct.unpack(">LL", png_bytes[16:24])
    return int(w), int(h)
