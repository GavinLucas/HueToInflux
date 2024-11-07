#!/usr/bin/env python3
""" Script to run iostat and send output to InfluxDB """

import os
import socket
import requests
import json
import datetime
from phue import Bridge

# load the settings.json file
with open("settings.json") as f:
    settings = json.load(f)

# get the local IP address
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.connect((settings["influx"]["host"], settings["influx"]["port"]))
IP = s.getsockname()[0].replace(".", "_")
s.close()


def connect_to_bridge():
    """
    Connect to the Hue bridge

    :return:
    :rtype:
    """
    try:
        b = Bridge(ip=settings["hue"]["host"], username=settings["hue"]["user"])
        b.connect()
        assert b.get_api()  # just to check if connection was successful
    except Exception as e:
        raise e
    return b


def get_sensors(b):
    upstairs = b.get_sensor()["14"]["state"]["temperature"]
    downstairs = b.get_sensor()["61"]["state"]["temperature"]
    timestamp = datetime.datetime.now()
    return timestamp, upstairs, downstairs


def parse_and_send(iostat_line):
    """Parses and sends a line of iostat data to influxDB"""
    # parse the line
    print(" ^", end="\r")  # minimalist activity indicator
    fields = iostat_line.split()
    if len(fields) == 23:
        device, *stats = fields
        metric_data = ",".join(
            f"{key}={float(value)}"
            for key, value in zip(
                (
                    "r_s",
                    "rkB_s",
                    "rrqm_s",
                    "rrqm",
                    "r_await",
                    "rareq_sz",
                    "w_s",
                    "wkB_s",
                    "wrqm_s",
                    "wrqm",
                    "w_await",
                    "wareq_sz",
                    "d_s",
                    "dkB_s",
                    "drqm_s",
                    "drqm",
                    "d_await",
                    "dareq_sz",
                    "f_s",
                    "f_await",
                    "aqu_sz",
                    "util",
                ),
                stats,
            )
        )
        data = f"iostat,host={IP},device={device} {metric_data}"

        # send to InfluxDB
        url = (
            f"http://{settings['influx']['host']}:{settings['influx']['port']}/"
            f"write?db={settings['influx']['db']}&precision=s"
        )
        try:
            response = requests.post(
                url,
                auth=(settings["influx"]["user"], settings["influx"]["password"]),
                data=data,
                timeout=5,
            )
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            print("Error sending data to InfluxDB: ", e)
            print(" _", end="\r")  # minimalist activity indicator


def main():
    """The main function"""
    # Get data from Hue hub

    # Format the data

    # Send the data to InfluxDB


if __name__ == "__main__":
    main()
