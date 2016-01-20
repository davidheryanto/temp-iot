from __future__ import print_function

import logging
import random
import re
import socket
import time
from collections import OrderedDict
from cloudant.account import Cloudant

import ibmiotf.device

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


def get_client(options=None):
    if options is None:
        options = {
            "org": 'km4ts7',
            "type": 'atrack',
            "id": '1234',
            "auth-method": 'token',
            "auth-token": 'DE5vHelsELG1SH46Ba'
        }
    client = ibmiotf.device.Client(options)
    logger.debug('Created client with configuration:')
    logger.debug(options)
    return client

def get_db_client(username, password):
    client = Cloudant(username, password, account=username)
    return client


def parse_atrack_msg(text):
    field_names = (
        "@P,CRC,L,Seq.ID,UNID,GPS time, RTC time, Position time, Lon, "
        "Lat, Heading, Report ID, Odo, HDOP, DI, Speed, DO, AI, DVID, "
        "1st Temp, 2nd Temp, Text").split(',')
    field_vals = text.split(',')
    logger.debug('field_vals: {}'.format(field_vals))
    out = OrderedDict([(k, v) for k, v in zip(field_names, field_vals)])
    out_processed = OrderedDict([
        ('device_id', out.get('UNID', -1)),
        ('driver_id', out.get('DVID', -1)),
        ('report_id', out.get('Report ID', -1)),
        ('timestamp', out.get('Position time', int(time.time()))),
        ('hdop', out.get('HDOP', 990)),
        ('latitude', float(out.get('Lon', 1300000)) / 1e6),
        ('longitude', float(out.get('Lat', 103800000)) / 1e6),
        ('heading', out.get('Heading', -1)),
        ('speed', out.get('Speed', -1)),
        ('odometer', out.get('Odo', -1)),
        ('temperature_1', out.get('1st Temp', -1)),
        ('temperature_2', out.get('2nd Temp', -1))
    ])
    logger.debug('Parse result:\n{}'.format(out_processed))
    return out_processed


def dummy_ibm_data():
    rand_data = {'name': 'foo',
                 'cpu': random.randrange(0, 51),
                 'mem': random.randrange(50, 101)}
    return rand_data


def main():
    # Setup IBM IoT client
    ibm_client = get_client()
    ibm_client.connect()
    logger.info('IBM IoT client connected')

    # Setup socket server
    host = ''
    port = 5000
    backlog = 5
    size = 4096
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((host, port))
    s.listen(backlog)

    logger.info('Socket server accepting connection ...')
    socket_client, address = s.accept()
    logger.info('Socket server connected to {}'.format(address))
    count = 0
    while 1:
        data = socket_client.recv(size)
        count += 1
        logger.debug('Received message #{}'.format(count))
        for line in data.split('\n'):
            if not line.startswith('@P'):
                break

            logger.debug(re.sub('\s+', ' ', data).strip())

            # data_to_send = dummy_ibm_data()
            data_to_send = parse_atrack_msg(line)
            ibm_client.publishEvent("status", "json", data_to_send)

            logger.debug('IBM client successfully published event:')
            logger.debug('{}'.format(data_to_send))

    socket_client.close()


if __name__ == '__main__':
    main()
