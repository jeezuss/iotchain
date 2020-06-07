LIC_DIR = 'lic/'
NUM_ZEROS = 4
NUM_ZEROS_LIC = 2

PEERS = [
    'http://127.0.0.1:5000/'
    ]

DATACH = 'Data from IoT'
DEVICE = 'local'
DEVICE_IP = '192.168.1.9'
DEVICE_PORT = 5001
LIC_VAR_CONVERSIONS = {'index': int, 'nonce': int, 'hash': str, 'prev_hash': str, 'timestamp': int, 'count': int, 'node': str, 'device_name': str}

STANDARD_ROUNDS = 100
CSV_COL = ['ip', 'port', 'device_name', 'count']
import os

class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'testkey'
