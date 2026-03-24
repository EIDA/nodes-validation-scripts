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
from obspy.core.inventory import Network, Station, Channel
from obspy.clients.fdsn import Client
from datetime import datetime


def list_stations(dc: dict, net: str):
    """
    builds a list of stations from a datacenter and a network
    """
    stations = [p["sta"] for p in dc["params"] if p["net"] == net]
    return stations


def get_restricted_status(net: Network, sta: Station, cha: Channel):
    """
    Determine "restricted status" of a channel, embedded in station and network
    objects. It is assumed that a) the restricted status set on inner nodes
    (e.g. Channel) overrules any potentially set restricted status set on outer
    nodes (e.g. Network) and b) that the default restricted status is "open".
    """
    # sanity check, make sure the provided items are actually nested
    if sta not in net or cha not in sta:
        raise ValueError('expected nested Network/Station/Channel')

    # if Channel has restricted status set, use that
    if cha.restricted_status is not None:
        level = 'channel'
        value = cha.restricted_status
    # fall back to Station and check restricted status there
    elif sta.restricted_status is not None:
        level = 'station'
        value = sta.restricted_status
    # fall back to Network and check restricted status there
    elif net.restricted_status is not None:
        level = 'network'
        value = net.restricted_status
    else:
        level = 'default'
        value = 'open'
    return level, value


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
                    r_level, r_status = get_restricted_status(net, sta, cha)
                    if r_status != 'open':
                        if cha.start_date < embargo_start:
                            restricted_channels.append(
                                f"{net.code}_{sta.code}_{cha.location_code}_{cha.code} [{r_level}:{r_status}] {cha.start_date} -> {cha.end_date}"
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
