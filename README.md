HueToInflux
===========

https://github.com/GavinLucas/HueToInflux
-----------------------------------------

Script to take data from a Hue Bridge and post it to InfluxDB in order to view the data in Grafana.

Currently, it collects presence, temperature and light readings from Hue Motion Sensors and the brightness 
of lights, but could be modified to collect other data from the Hue Bridge.

To create a username and password for the Hue Bridge, follow the instructions 
here: https://developers.meethue.com/develop/get-started-2/

To run the script:
- copy settings.json.example to settings.json
  - Change the permissions of the file, e.g. `chmod 600 settings.json`, so that it's not readable 
  by other users
  - Fill in the values for your Hue Bridge and InfluxDB
  - Set the 'interval' to the number of seconds between each data collection
  - The 'sensors' section is for remapping the names of sensors if you're not happy with the names in the 
  Hue settings.  This is optional
- Install the requirements with `pip install -r requirements.txt`
- Leave the script running in a screen session and sit back and watch the data roll in.

There are a couple of options that can be passed to the script to help you understand your data:

- To dump all the data from the Hue Bridge in order to see the names, etc., run `huetoinflux.py --dump` 
and it will output all the data returned as json.
- To print the data rather than send it to InfluxDB, run `huetoinflux.py --print` and it will output the
parsed data structure as json.
