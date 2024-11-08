HueToInflux
===========

Script to take data from a Hue hub and post it to InfluxDB in order to view the data in Grafana.

Currently, it collects temperature and light readings from Hue Motion Sensors, but could be modified to collect other data from the Hue hub.

To create a username and pasword for the Hue hub, follow the instructions here: https://developers.meethue.com/develop/get-started-2/

- To run the script, copy settings.json.example to settings.json and fill in the values.  
- Install the requirements with `pip install -r requirements.txt`
- Leave it running in a screen session and sit back and watch the data roll in.