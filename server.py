# server side
from typing import Union
from fastapi import FastAPI

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

@app.get("/adapters")
async def adapters_data():
    netdata = network_adapters_data(cmd="")
    return netdata

@app.get("/numatopo")
async def adapters_data():
    netdata = network_adapters_data(cmd="")
    return netdata
