#!/usr/bin/env python3
# /// script
# requires-python = "==3.12.*"
# dependencies = [
#     "obspy>=1.4.2",
#     "requests",
#     "setuptools<82",
# ]
# ///

import requests
from obspy.clients.fdsn import Client
from datetime import datetime


def list_stations(dc: dict, net: str):
    """
    builds a list of stations from a datacenter and a network
    """
    stations = [p["sta"] for p in dc["params"] if p["net"] == net]
    return stations


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
        adarray_stations = list_stations(svc, net)
        client = Client(base_url=url.removesuffix("fdsnws/station/1/query"))
        inventory = client.get_stations(
            net=net, level="channel", sta=",".join(adarray_stations)
        )

        for net in inventory.networks:
            for sta in net.stations:
                for cha in sta:
                    if cha.restricted_status == "closed":
                        if cha.start_date < embargo_start:
                            restricted_channels.append(
                                f"{net.code}_{sta.code}_{cha.location_code}_{cha.code} [{cha.restricted_status}] {cha.start_date} -> {cha.end_date}"
                            )

    if len(restricted_channels) > 0:
        print("## ", url)
        print("<details>")
        print(
            f"<summary>{len(restricted_channels)} channels need to be rolled out</summary>"
        )
        print()
        for c in restricted_channels:
            print(f"- {c}")
        print("</details>")
        print()
