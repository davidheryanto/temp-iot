import paho.mqtt.client as mqtt
import json
import time
import random

client = mqtt.Client('d:quickstart:atrack:9u0192u301u2093u102981')
client.connect("quickstart.messaging.internetofthings.ibmcloud.com", 1883, 60)
topic = 'iot-2/evt/status/fmt/json'

while 1:
    time.sleep(3)
    msg = json.JSONEncoder().encode({'d': {
        'value': random.randrange(0, 101),
    }})
    client.publish(topic,msg)
    print('Message published: {}'.format(msg))
