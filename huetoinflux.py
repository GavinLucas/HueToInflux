#!/usr/bin/env python3
""" Script to run iostat and send output to InfluxDB """

import sys
import time
import json
import signal
import socket
import argparse
import requests
import phue

# load the settings.json file
try:
    with open("settings.json", encoding="utf8") as f:
        settings = json.load(f)
except FileNotFoundError:
    print("settings.json not found.")
    print("Make sure you copy settings.json.example to settings.json and edit it.")
    sys.exit(1)


def signal_handler(sig, frame):
    """
    Signal handler to exit gracefully
    """
    # avoid unused variable warning
    if frame:
        pass

    # print a message and exit
    print(f"\nExiting on signal {sig}")
    sys.exit(0)


def get_data_from_bridge():
    """
    Connect to the Hue bridge and get the sensor data

    :return: hue_data
    :rtype: dict
    """
    try:
        hue = phue.Bridge(ip=settings["hue"]["host"], username=settings["hue"]["user"])
        hue.connect()
        hue_data = hue.get_api()
    except (socket.gaierror, ConnectionRefusedError, phue.PhueRequestTimeout) as e:
        print(f"Error connecting to Hue Bridge - {e}")
        sys.exit(2)
    if isinstance(hue_data, list) and "error" in hue_data[0]:
        print(f"Error connecting to Hue Bridge - {hue_data[0]['error']['description']}")
        sys.exit(2)
    return hue_data


def device_name_to_name(device_name):
    """
    Converts the device name into a name to be used in InfluxDB

    If no name mapping exists in the settings file, the name in the Hue settings is used.
    Any spaces will be replaced with underscores.

    :param device_name: name of the device in the hue settings
    :type device_name: str
    :return: name
    :rtype: str
    """
    name = settings["sensors"].get(device_name, device_name) if "sensors" in settings else device_name
    return name.replace(" ", "_")


def parse_data():
    """
    Parse the data from the bridge to get the values we want

    :return: data
    :rtype: dict
    """
    data = {}
    hue_data = get_data_from_bridge()

    # parse the sensor data
    for device in hue_data["sensors"].values():
        name = device_name_to_name(device["name"])
        if device["type"] == "ZLLTemperature":
            # convert temperature to the desired units
            celsius = device["state"]["temperature"] / 100
            if settings.get("temperature_units") == "F":
                data[name] = round((celsius * 1.8) + 32, 2)
            elif settings.get("temperature_units") == "K":
                data[name] = round(celsius + 273.15, 2)
            else:
                data[name] = round(celsius, 2)
        elif device["type"] == "ZLLLightLevel":
            # convert light level to lux
            data[name] = round(float(10 ** ((device["state"]["lightlevel"] - 1) / 10000)), 2)
        elif device["type"] == "ZLLPresence":
            # convert presence to boolean 0 or 1
            data[name] = int(1 if device["state"]["presence"] else 0)

    for device in hue_data["lights"].values():
        name = device_name_to_name(device["name"])
        # convert brightness to percentage if the light is dimmable (has a "bri" attribute)
        # otherwise boolean 0 or 1 to cover smart plugs which are also listed as lights
        data[name] = int(device["state"].get("bri", 2.54) / 2.54) if device["state"]["on"] else 0

    return data


def send_data_to_influx(data):
    """
    Sends data to influxDB

    :param data: data to send to InfluxDB
    :type data: dict
    :return: None
    """

    # minimalist activity indicator
    print(" ^", end="\r")

    # format the data to send
    data_to_send = f"hue,host={settings['hue']['host']} " + ",".join([f"{key}={value}" for key, value in data.items()])

    # send to InfluxDB
    url = f"{settings['influx']['url']}/write?db={settings['influx']['db']}&precision=s"
    try:
        response = requests.post(
            url,
            auth=(settings["influx"]["user"], settings["influx"]["password"]),
            data=data_to_send,
            timeout=settings["influx"].get("timeout", 5),
        )
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"Error sending data to InfluxDB - {e}")

    # minimalist activity indicator
    print(" _", end="\r")


def main():
    """
    The main function
    """

    # register the signal handler for ctrl-c
    signal.signal(signal.SIGINT, signal_handler)

    # parse the command line arguments
    arg_parse = argparse.ArgumentParser(description="Send Hue Data to InfluxDB")
    arg_parse.add_argument(
        "-d",
        "--dump",
        required=False,
        action="store_true",
        help="dump the data from the Hue bridge to the console",
    )
    arg_parse.add_argument(
        "-p",
        "--print",
        required=False,
        action="store_true",
        help="print the data rather than sending it to InfluxDB",
    )
    args = arg_parse.parse_args()

    # dump the data if required and exit
    if args.dump:
        hue_data = get_data_from_bridge()
        print(json.dumps(hue_data, indent=4))
        sys.exit(0)

    # main loop to collect and send data to InfluxDB
    next_update = time.time()
    while True:
        next_update += settings["interval"]

        # get the parsed data
        data = parse_data()

        # print or send the data
        if args.print:
            blob = {"time": time.strftime("%a, %d %b %Y, %H:%M:%S %Z", time.localtime()), "data": data}
            print(json.dumps(blob, indent=4))
        else:
            send_data_to_influx(data)

        # Sleep until the next interval
        sleep_time = max(0, next_update - time.time())
        time.sleep(sleep_time)


if __name__ == "__main__":
    main()
