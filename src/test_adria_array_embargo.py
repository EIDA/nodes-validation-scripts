#!/usr/bin/env python3
# /// script
# requires-python = "==3.12.*"
# dependencies = [
#     "obspy>=1.4.2",
#     "requests",
#     "setuptools<82",
# ]
# ///

import sys
import requests
from datetime import datetime
from obspy.clients.fdsn import Client
import xml.etree.ElementTree as ET

# First fetch ADRIA ARRAY stations from the routing
resp = requests.get(
    "https://www.orfeus-eu.org/eidaws/routing/1/query?service=station&network=_ADARRAY&format=json"
)
inventory = resp.json()

# Embargo should start 2 years before now
embargo_start = datetime(datetime.now().year - 2, 1, 1)

for svc in inventory:
    url = svc["url"]
    # Make a unique list of networks
    restricted_channels = []

    networks = set([n["net"] for n in svc["params"]])
    for net in networks:
        client = Client(base_url=url.removesuffix("fdsnws/station/1/query"))
        inventory = client.get_stations(net=net, level="channel")

        for net in inventory.networks:
            for sta in net.stations:
                for cha in sta:
                    if cha.restricted_status == "closed":
                        if cha.start_date < embargo_start:
                            restricted_channels.append(cha)

    if len(restricted_channels) > 0:
        print("## ", url)
        for cha in restricted_channels:
            print(
                f"{net.code}_{sta.code}_{cha.location_code}_{cha.code}: {cha.start_date} -> {cha.end_date}"
            )
