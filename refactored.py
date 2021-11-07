import json
import requests
import logging
from datetime import datetime
import time
import os

import paho.mqtt.client as mqtt


station    = os.environ['station']
useMQTT    = os.environ['useMQTT']
mqttBroker = os.environ['mqttBroker']
mqttUser   = os.environ['mqttUser']
mqttPass   = os.environ['mqttPass']
mqttBase   = os.environ['mqttBase']

#print("Running with the following ENVs")
#print("Station : " + station)
#print("useMqtt : " + useMQTT)
#print("mqttBroker : " + mqttBroker)
#print("mqttUser : " + mqttUser)
#print("mqttPass : " + mqttPass)
#print("mqttBase : " + mqttBase)

if station == "station":
    print("You will need to configure the station ID")
    quit()


##################
# Logging Stuff  #
##################

#logging.basicConfig()
logging.basicConfig(filename="FloodMonitor.log", format='%(asctime)s [%(levelname)s] %(message)s', level=logging.DEBUG)
logging.info("+---------------------------------------------------------------------------+")
logging.info("| River Level Monitor                                                  V2.0 |")
logging.info("|                                                                           |")
logging.info("| Program that uses the Environment Agency's open API to read the river     |")
logging.info("| level from the local river monitor / flood alerts.                        |")
logging.info("|                                                                           |")
logging.info("| Author : Jimmy Kemp                                      Date: 27/06/2021 |")
logging.info("|                                                                           |")
logging.info("| Contains public sector information licensed under the                     |")
logging.info("| Open Government Licence v3.0.                                             |")
logging.info("| http://www.nationalarchives.gov.uk/doc/open-government-licence/version/3/ |")
logging.info("+---------------------------------------------------------------------------+")
logging.debug("Started program")

def getRiverLevel(riverStation):
    baseUrl = "https://environment.data.gov.uk/flood-monitoring/id/stations/"
    url = baseUrl + riverStation
    logging.debug("Called getRiverLevel")

    try:
        response = requests.get(url)
        if response.status_code == 200:
            return json.loads(response.content.decode('utf-8'))
        else:
            return None
    except:
        logging.warning("Unable to fetch results")


##############
# MQTT Stuff #
##############

mqtt.Client.connected_flag=False                                    #create flag in class
client = mqtt.Client()         

def on_subscribe(client, userdata, mid, granted_qos):
    logging.debug(granted_qos)

def on_connect(client, userdata, flags, rc):
    if rc==0:
        client.connected_flag=True #set flag
        logging.debug("MQTT: Connected OK Returned code=" + str(rc))
        #client.subscribe(topic)
    else:
        print("MQTT: Bad connection Returned code= " + str(rc))


def on_message(client, userdata, message):
    #global displayFlag, displayFlagSet
    print("message received " ,str(message.payload.decode("utf-8")))
    print("message topic=",message.topic)
    print("message qos=",message.qos)
    print("message retain flag=",message.retain)

    if (message.topic == "house/alert/msg"):
        print ("Alert: " + message.payload.decode("utf-8"))
        
        
        displayFlag = 1
        displayFlagSet = time.time()

    #if (message.topic == "house/floodMonitor/brightness"):
    #    bright = int(message.payload.decode("utf-8"))
    #    setBrightness(bright)

    
def connectMQTT (broker, mqttuser, mqttpass, baseTopic):
    global client

    mqttBroker = broker

          
    if mqttuser !='' or mqttpass != '':
        client.username_pw_set(username=mqttUser,password=mqttPass)
    client.on_connect=on_connect                                        #bind call back function
    client.on_message=on_message                                        #attach function to callback
    client.on_subscribe=on_subscribe

    #show_message(device, "Connecting to the Broker...", fill="white", font=proportional(SINCLAIR_FONT))
    client.loop_start()

    print("Connecting to broker ",mqttBroker)
    client.connect(mqttBroker)                                          #connect to broker
    while not client.connected_flag:                                    #wait in loop
        print("In wait loop")
        time.sleep(1)
    print("Connected")
    #show_message(device, "Connected!", fill="white", font=proportional(SINCLAIR_FONT))

    print("Subscribing to topic " + baseTopic + "/#")
    result = client.subscribe(baseTopic + "/#", 0)
    print(result)
    

print("Checking to see if need to connect to MQTT")
if useMQTT == "TRUE":
    connectMQTT(mqttBroker, mqttUser, mqttPass, mqttBase)
    print(client.connected_flag)


print("Running App: Entering Loop")
running = True
lastReading = ''
checkedLevel = "firstRun"

while running :
    now = datetime.today()
    minute = now.strftime("%M")
    second = now.strftime("%S")

    if minute == '00' or minute == '15' or minute == '30' or minute == '45' or checkedLevel == "firstRun":
        if checkedLevel == False or checkedLevel == "firstRun": 

            checkedLevel = True

            riverStationInfo = getRiverLevel(station)
            if riverStationInfo is not None:
                #Check to see how many results as there are multiples in the one I am interested in now...
                returnedType = type(riverStationInfo['items']['measures'])

                if returnedType == list:
                    print ("Its a list")
                    numResults =  len(riverStationInfo['items']['measures'])
                    if numResults > 1:
                        for x in range(numResults):
                            if riverStationInfo['items']['measures'][x]['unitName'] == "m" :
                                riverStatusItem = riverStationInfo['items']['measures'][x]
                    
                    else:
                        riverStatusItem = riverStationInfo['items']['measures']

                else:
                    print("Its not a list")
                    riverStatusItem = riverStationInfo['items']['measures']
                
                latestReading = riverStatusItem['latestReading']['value']
                latestReadingDateTime = riverStatusItem['latestReading']['dateTime']
    
            if latestReadingDateTime != lastReading:
                lastReading = latestReadingDateTime
                logging.debug("Date Time changed")
                logging.info("New Value, " + str(latestReading))
                print(latestReadingDateTime + " : " + str(latestReading))
                riverStationID = riverStatusItem['stationReference']
                client.publish("house/riverLevel/"+riverStationID, str(latestReading), qos=0, retain=True)
            
            else:
                logging.debug("Checked, but no new info!")
    else:
        checkedLevel = False

    #print(str(now) + " - " + str(checkedLevel))
    time.sleep(1)
