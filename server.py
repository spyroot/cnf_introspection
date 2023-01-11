# server side, so you can hook up ansible etc.
import io

from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from interspect.network_data import network_adapters_data
import json

from interspect.stat import cpu_per_core

app = FastAPI()

@app.get("/")
def read_root():
    return {}


@app.get("/adapters")
async def adapters_data():
    """Network data
    :return:
    """
    netdata = network_adapters_data(cmd="")
    return netdata


@app.get("/numa.svg")
async def adapters_data(topo_file="/tmp/topo.svg"):
    """Output numa topology svg
    :param topo_file:
    :return:
    """
    with open(topo_file, "rb") as fh:
        buf = io.BytesIO(fh.read())
        image_stream = io.BytesIO(buf.read())
    return StreamingResponse(content=image_stream, media_type="image/svg+xml")

@app.get("/cpu_stat")
async def adapters_data():
    """
    :return:
    """
    return cpu_per_core(cmd="")

@app.get("/numatopo")
async def adapters_data():
    """
    :return:
    """
    netdata = network_adapters_data(cmd="")
    return netdata
