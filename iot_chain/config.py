CHAINDATA_DIR = 'chaindata/'
NUM_ZEROS = 5

PEERS = [
    'http://192.168.1.9:5000/','http://192.168.1.9:5002/'
    ]
COMMAND = {'from': 'node2','to': 'node1', 'com': 'http://192.168.1.2:8123/api/states/sensor.cpu_temp'}
MAIN_COUNT = 7
DEVICE_NAME = 'node2'
DEVICE_IP = '192.168.1.9'
DEVICE_PORT = 5002
LIC_IP = 'http://192.168.1.9:5001/'
DATACH = "utils.make_data('DATA from 192.168.1.1', '192.168.1.1')"

BLOCK_VAR_CONVERSIONS = {'index': int, 'nonce': int, 'hash': str, 'prev_hash': str, 'timestamp': int}

STANDARD_ROUNDS = 1000000

import os

class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'testkey'
