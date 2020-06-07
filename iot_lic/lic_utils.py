from config import *
import datetime
import hashlib
import lic_block
import os
import glob
import json
import chain
import csv
import pandas as pd


def dict_from_block_attributes(**kwargs):
    info = {}
    for key in kwargs:
        if key in LIC_VAR_CONVERSIONS:
            info[key] = LIC_VAR_CONVERSIONS[key](kwargs[key])
        else:
            info[key] = kwargs[key]
    return info


def generate_hash(password):
    hash_object = hashlib.sha256(password.encode('utf-8')).hexdigest()
    # hex_dig = hash_object.hexdigest()
    return hash_object


def create_new_block_from_prev(prev_block=None, device_name='local', node=None, count=0, timestamp=None):
    if not prev_block:
        # index zero and arbitrary previous hash
        index = 0
        prev_hash = ''
    else:
        index = int(prev_block.index) + 1
        prev_hash = prev_block.hash

    if not node:
        node = DATACH

    if not device_name:
        device_name = DEVICE

    if not timestamp:
        timestamp = datetime.datetime.utcnow().strftime('%Y%m%d%H%M%S%f')
    nonce = 0
    block_info_dict = dict_from_block_attributes(index=index, timestamp=timestamp, device_name=device_name, node=node, count=count,
                                                 prev_hash=prev_hash,
                                                 nonce=nonce)
    new_block = lic_block.Block(block_info_dict)
    return new_block


def find_valid_nonce(find_block, node=None):
    find_block.nonce = 0
    find_block.update_self_hash()  # calculate_hash(index, prev_hash, node, count, timestamp, nonce)
    if not find_block.node:
        find_block.node = node
    while str(find_block.hash[0:NUM_ZEROS_LIC]) != '0' * NUM_ZEROS_LIC:
        find_block.nonce += 1
        find_block.update_self_hash()
    assert find_block.is_valid()
    return find_block


def get_nodes():
    blocks = []
    # We're assuming that the folder and at least initial block exists
    if os.path.exists(LIC_DIR):
        for filepath in glob.glob(os.path.join(LIC_DIR, '*.json')):
            with open(filepath, 'r') as block_file:
                try:
                    block_info = json.load(block_file)
                except:
                    print(filepath)
                local_block = lic_block.Block(block_info)
                blocks.append(local_block)
    blocks.sort(key=lambda block: block.index)
    local_chain = chain.Chain(blocks)
    return local_chain


def get_node(nod):
    blocks = {}
    # We're assuming that the folder and at least initial block exists
    if os.path.exists(LIC_DIR):
        for filepath in glob.glob(os.path.join(LIC_DIR, '*.json')):
            with open(filepath, 'r') as block_file:
                try:
                    block_info = json.load(block_file)
                except:
                    print(filepath)
                print(block_info['index'])
                if int(block_info['index']) == int(nod):
                    blocks = block_info
    return blocks


def mine_for_block(chain=None, rounds=STANDARD_ROUNDS, start_nonce=0, timestamp=None, node='localhost', device_name='local'):
    if not chain:
        chain = get_nodes()  # gather last node
    prev_block = chain.most_recent_block()
    return mine_from_prev_block(prev_block, rounds=rounds, start_nonce=start_nonce, timestamp=timestamp, node=node, device_name=device_name)


def mine_from_prev_block(prev_block, rounds=STANDARD_ROUNDS, start_nonce=0, timestamp=None, node=None, device_name='local'):
    # create new block with correct
    new_block = create_new_block_from_prev(prev_block=prev_block, timestamp=timestamp, node=node, device_name=device_name)
    return mine_block(new_block, rounds=rounds, start_nonce=start_nonce)


def mine_block(new_block, rounds=STANDARD_ROUNDS, start_nonce=0):
    print("Mining for block %s. start_nonce: %s, rounds: %s" % (new_block.index, start_nonce, rounds))
    # Attempting to find a valid nonce to match the required difficulty
    # of leading zeros. We're only going to try 1000
    while str(new_block.hash[0:NUM_ZEROS]) != '0' * NUM_ZEROS:
        start_nonce = start_nonce + 1
        new_block.nonce = start_nonce
        new_block.update_self_hash()
        if str(new_block.hash[0:NUM_ZEROS]) == '0' * NUM_ZEROS:
            print("block %s mined. Nonce: %s" % (new_block.index, new_block.nonce))
            assert new_block.is_valid()
            new_block.self_save()
            return new_block, rounds, start_nonce, new_block.timestamp
    # couldn't find a hash to work with, return rounds and start_nonce
    # as well so we can know what we tried
    return None, rounds, start_nonce, new_block.timestamp


def add_to_json(data):
    js_data = {}
    if os.path.exists('nodes.json'):
        if os.path.getsize('nodes.json') > 0:
            with open('nodes.json', 'r') as f:
                js_data = json.load(f)
            with open('nodes.json', 'w') as f:
                index = len(js_data) + 1
                js_data.update({index: data})
                json.dump(js_data,f)
        else:
            with open('nodes.json', 'w') as f:
                index = 1
                js_data.update({index: data})
                json.dump(js_data,f)


def add_com_to_json(data):
    if os.path.exists('commands.json'):
        with open('commands.json', 'r') as f:
            js_data = json.load(f)
        with open('commands.json', 'w') as f:
            index = len(js_data) + 1
            js_data.update({index: data})
            json.dump(js_data, f)


def checker_json(device_name):
    i = 0
    if os.path.exists('nodes.json') and os.path.getsize('nodes.json') > 0:
        with open('nodes.json', 'r') as f:
            data = json.load(f)
            for index in range(len(data)):
                if data[str(index+1)]['device_name'] == device_name:
                    i = 1
    return i


def update_count(device_name, count):
    if os.path.exists('nodes.json'):
        with open('nodes.json', 'r') as f:
            data = json.load(f)
            for index in range(len(data)):
                if data[str(index + 1)]['device_name'] == device_name:
                    data[str(index + 1)]['count'] = int(data[str(index + 1)]['count']) + count
        with open('nodes.json', 'w') as f:
            json.dump(data, f)


def get_peers():
    list_peers = {}
    if os.path.exists('nodes.json'):
        with open('nodes.json', 'r') as f:
            data = json.load(f)
            for index in range(len(data)):
                inf = 'http://'+data[str(index + 1)]['ip']+':'+data[str(index + 1)]['port']
                list_peers.update({index: inf})
    return list_peers



def get_device_name():
    list_peers = {}
    if os.path.exists('nodes.json'):
        with open('nodes.json', 'r') as f:
            data = json.load(f)
            for index in range(len(data)):
                inf = data[str(index + 1)]['device_name']
                list_peers.update({index: inf})
    return list_peers


def get_count(device_name):
    device_count = -1
    if os.path.exists('nodes.json'):
        with open('nodes.json', 'r') as f:
            data = json.load(f)
            for index in range(len(data)):
                if data[str(index + 1)]['device_name'] == device_name:
                    device_count = int(data[str(index + 1)]['count'])
    return device_count
