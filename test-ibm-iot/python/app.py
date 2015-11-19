import ibmiotf.device
import random
import time

options = {
    "org": 'km4ts7',
    "type": 'atrack',
    "id": '1234',
    "auth-method": 'token',
    "auth-token": 'DE5vHelsELG1SH46Ba'
}
client = ibmiotf.device.Client(options)

client.connect()

while 1:
    time.sleep(2)
    myData = {'name': 'foo',
              'cpu': random.randrange(0, 51),
              'mem': random.randrange(50, 101)}
    client.publishEvent("status", "json", myData)
