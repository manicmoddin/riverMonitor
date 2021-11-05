# River Monitor

Python3 app that will check the envionment Agencies open API to grab the latest river level for a predetermined monitoring station

## Configuration
As this is a docker image, you will need to set some env vars, failing to do so will result in the following error in the logs:

You will need to configure the station ID

Valid ENV vars are:

- station - the stationID you are interested in
- useMQTT - if you are wanting MQTT (TRUE / FALSE) - **has to be all caps**
- mqttBroker - MQTT Broker Address
- mqttUser - MQTT username - omit if not required
- mqttPass - MQTT password - omit if not required
- mqttBase - MQTT Base topic

### Finding out the stationID to use
To find the stationID that you are interested in, the envronment agency publish a json list of all the stations on the following link

https://environment.data.gov.uk/flood-monitoring/id/stations

This can be filtered using long / lat, river names, or station names etc as per the help that is linked in the above URL

## MQTT
This will also publish the returned river level to MQTT should you enable and configure a base topic in MQTT.

## Building
To build the image, once extracted:
1. Move to the file with the Dockerfile in it.
2. Run `docker build -t river_monitor_img .`

the dot(.) at the end is important

## Running
When ready to run, run the following command, subsituting the right details in

`docker run -tid --rm --name riverMonitor -e station=<stationID> -e userMQTT=<TRUE> -e mqttBroker="<BROKERADDRESS>" -e mqttUser=<username> -e mqttPass=<password> -e mqttBase=<baseTopic> river_monitor_img`

# Disclaimer
There is no warranty with this at all, nothing, zip, nada.
If you run and the river revel is different to what is mentioned, if really not my fault, if you run this and bad things happen, its very unlikely related, but if it was related, I take no responsibilty.
This software will not ever replace the need to physically check the local river levels if not for anything else, but a walk in nature.
