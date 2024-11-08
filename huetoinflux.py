#!/usr/bin/env python3
""" Script to run iostat and send output to InfluxDB """

import time
import requests
import json
from phue import Bridge

# load the settings.json file
with open("settings.json") as f:
    settings = json.load(f)

SENSORS = {
    "Hue ambient light sensor 1": "Kitchen_Light_Sensor",
    "Hue ambient light sensor 2": "Hall_Light_Sensor",
    "Hue ambient light sensor 3": "Landing_Light-Sensor",
    "Hue ambient light sensor 4": "Toilet_Light_Sensor",
    "Hue ambient light sensor 5": "Conservatory_Light_Sensor",
    "Hue temperature sensor 1": "Kitchen_Temperature_Sensor",
    "Hue temperature sensor 2": "Hall_Temperature_Sensor",
    "Hue temperature sensor 3": "Landing_Temperature_Sensor",
    "Hue temperature sensor 4": "Toilet_Temperature_Sensor",
    "Hue temperature sensor 5": "Conservatory_Temperature_Sensor",
}


def get_data_from_bridge():
    """
    Connect to the Hue bridge and get the sensor data

    :return: hue_data
    :rtype: dict
    """
    try:
        hue_data = Bridge(ip=settings["hue"]["host"], username=settings["hue"]["user"])
        hue_data.connect()
        assert hue_data.get_api()  # just to check if connection was successful
    except Exception as e:
        raise e
    return hue_data.get_sensor()


def sensor_name_to_name(sensor_name):
    """
    Convert the sensor name to a more human-readable name

    :param sensor_name: The name of the sensor
    :type sensor_name: str

    :return: name
    :rtype: str
    """
    name = SENSORS.get(sensor_name)
    return name


def send_data_to_influx(data):
    """Parses and sends a line of iostat data to influxDB

    :param data: data to send to InfluxDB
    :type data: dict

    :return: None
    """
    # format the data to senddata_to_send = f"hue,host={IP} {data}"
    # print(" ^", end="\r")  # minimalist activity indicator
    data_to_send = f"hue,host={settings["hue"]["host"]} " + ",".join([f"{key}={value}" for key, value in data.items()])

    # send to InfluxDB
    url = (
        f"http://{settings['influx']['host']}:{settings['influx']['port']}/"
        f"write?db={settings['influx']['db']}&precision=s"
    )
    try:
        response = requests.post(
            url,
            auth=(settings["influx"]["user"], settings["influx"]["password"]),
            data=data_to_send,
            timeout=5,
        )
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print("Error sending data to InfluxDB: ", e)
        print(" _", end="\r")  # minimalist activity indicator


def main():
    """The main function"""

    next_update = time.time()
    while True:
        next_update = next_update + settings["interval"]
        data = {}
        hue_data = get_data_from_bridge()
        for device in hue_data:
            if hue_data[device]["type"] == "ZLLTemperature":
                name = sensor_name_to_name(hue_data[device]["name"])
                data[name] = round(hue_data[device]["state"]["temperature"] / 100, 2)
            elif hue_data[device]["type"] == "ZLLLightLevel":
                name = sensor_name_to_name(hue_data[device]["name"])
                data[name] = round(float(10 ** ((hue_data[device]["state"]["lightlevel"] - 1) / 10000)), 2)
        send_data_to_influx(data)

        # Sleep until the next interval
        sleep_time = max(0, next_update - time.time())
        time.sleep(sleep_time)


if __name__ == "__main__":
    main()
