# server side
import io

from fastapi import FastAPI
from fastapi.responses import StreamingResponse

from interspect.network_data import network_adapters_data
import json

app = FastAPI()


@app.get("/")
def read_root():
    return {}

@app.get("/adapters")
async def adapters_data():
    netdata = network_adapters_data(cmd="")
    return netdata

@app.get("/numa")
async def adapters_data(topo_file = "/tmp/topo.svg"):
    """

    :param topo_file:
    :return:
    """
    with open(topo_file, "rb") as fh:
        buf = io.BytesIO(fh.read())
    image_stream = io.BytesIO(buf)
    return StreamingResponse(content=buf, media_type="image/svg")

@app.get("/numatopo")
async def adapters_data():
    """

    :return:
    """
    netdata = network_adapters_data(cmd="")
    return netdata
