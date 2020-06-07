import datetime
import time
import sync
import json
import hashlib
import requests
import os
import glob

from block import Block
from config import *
import utils

import apscheduler
from apscheduler.schedulers.blocking import BlockingScheduler

# if we're running mine.py, we don't want it in the background
# because the script would return after starting. So we want the
# BlockingScheduler to run the code.
sched = BlockingScheduler(standalone=True)

import logging
import sys

logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)

with open('chaindata/data.txt', 'r') as f:
    command_count = f.read()


def find_data():
    global command_count
    if os.path.exists('curr_commands.json') and os.path.getsize('curr_commands.json') > 0:
        with open('curr_commands.json', 'r') as f:
            data = json.load(f)
            if int(command_count) <= len(data):
                return True
            else:
                return False
    else:
        return False


if find_data() == True:
    data = ''
    with open('curr_commands.json', 'r') as f:
        js_data = json.load(f)
    required_com = ['command']
    required_rep = ['reply']
    if all(k in js_data[str(command_count)] for k in required_com):
        data = {'from': DEVICE_NAME, 'to': js_data[str(command_count)]['to'],
                'command': js_data[str(command_count)]['command']}
    elif all(k in js_data for k in required_rep):
        data = {'from': js_data[str(command_count)]['from'], 'to': js_data[str(command_count)]['to'],
                'command': js_data[str(command_count)]['reply']}
else:
    data = 'Node '+ DEVICE_NAME + ' is running'
    command_count = int(command_count) - 1


def mine_for_block(chain=None, rounds=STANDARD_ROUNDS, start_nonce=0, timestamp=None):
    if not chain:
        chain = sync.sync_local()  # gather last node
    prev_block = chain.most_recent_block()
    return mine_from_prev_block(prev_block, rounds=rounds, start_nonce=start_nonce, timestamp=timestamp)


def mine_from_prev_block(prev_block, rounds=STANDARD_ROUNDS, start_nonce=0, timestamp=None):
    # create new block with correct
    new_block = utils.create_new_block_from_prev(prev_block=prev_block, timestamp=timestamp, data=data)
    return mine_block(new_block, rounds=rounds, start_nonce=start_nonce)


def mine_block(new_block, rounds=STANDARD_ROUNDS, start_nonce=0):
    print("Mining for block %s. start_nonce: %s, rounds: %s" % (new_block.index, start_nonce, rounds))
    # Attempting to find a valid nonce to match the required difficulty
    # of leading zeros. We're only going to try 1000
    nonce_range = [i + start_nonce for i in range(rounds)]
    for nonce in nonce_range:
        new_block.nonce = nonce
        new_block.update_self_hash()
        if str(new_block.hash[0:NUM_ZEROS]) == '0' * NUM_ZEROS:
            broadcast_check(new_block)
            print("block %s mined. Nonce: %s" % (new_block.index, new_block.nonce))
            assert new_block.is_valid()
            return new_block, rounds, start_nonce, new_block.timestamp

    # couldn't find a hash to work with, return rounds and start_nonce
    # as well so we can know what we tried
    return None, rounds, start_nonce, new_block.timestamp


def mine_for_block_listener(event):
    global command_count
    global data
    # need to check if the finishing job is the mining
    if event.job_id == 'mining':
        new_block, rounds, start_nonce, timestamp = event.retval
        # if didn't mine, new_block is None
        # we'd use rounds and start_nonce to know what the next
        # mining task should use
        if new_block:
            if broadcast_check(new_block):
                print("Mined a new block")
                give_reward()
                take_penalty()
                new_block.self_save()
                broadcast_mined_block(new_block)
                command_count = str(int(command_count) + 1)
                with open('chaindata/data.txt', 'w') as f:
                    f.write(command_count)
                while find_data() == False:
                    time.sleep(5)
                with open('curr_commands.json', 'r') as f:
                    js_data = json.load(f)
                required_com = ['command']
                required_rep = ['reply']
                if all(k in js_data[str(command_count)] for k in required_com):
                    data = {'from': DEVICE_NAME, 'to': js_data[str(command_count)]['to'],
                        'command': js_data[str(command_count)]['command']}
                elif all(k in js_data[str(command_count)] for k in required_rep):
                    data = {'from': js_data[str(command_count)]['from'], 'to': js_data[str(command_count)]['to'],
                            'reply': js_data[str(command_count)]['reply']}
                sched.add_job(mine_from_prev_block, args=[new_block], kwargs={'rounds': STANDARD_ROUNDS, 'start_nonce': 0},
                              id='mining')  # add the block again
            else:
                print("Not enouth node to verify")
        else:
            print(event.retval)
            sched.add_job(mine_for_block,
                          kwargs={'rounds': rounds, 'start_nonce': start_nonce + rounds, 'timestamp': timestamp},
                          id='mining')  # add the block again
            sched.print_jobs()


def broadcast_mined_block(new_block):
    #  We want to hit the other peers saying that we mined a block
    block_info_dict = new_block.__dict__
    for peer in PEERS:
        endpoint = "%s/%s" % (peer[0], peer[1])
        # see if we can broadcast it
        try:
            r = requests.post(peer + 'mined', json=block_info_dict)
        except requests.exceptions.ConnectionError:
            print("Peer %s not connected" % peer)
            continue
    return True


def broadcast_check(new_block):
    block_info_dict = new_block.__dict__
    global_count = 0
    i = 0
    tmp_data = {}
    for peer in PEERS:
        endpoint = "%s/%s" % (peer[0], peer[1])
        # see if we can broadcast it
        try:
            reply = requests.post(peer + 'check_hash', json=block_info_dict).json()
            data = {'device_name': reply['device_name']}
            lic_reply = requests.post(LIC_IP + 'get_count', json=data).json()
            count = lic_reply['message']
            if count>=MAIN_COUNT:
                pen = count-MAIN_COUNT+1
                count = count - pen
                pen = -pen
                d = {'device_name': reply['device_name'], 'count': pen}
                rep = requests.post(LIC_IP + 'update_count', json=d)
            print(count)
            global_count += int(count)
            print(global_count)
            index = i + 1
            tmp_data.update({int(index): data})
            i += 1
        except requests.exceptions.ConnectionError:
            print("Peer %s not connected" % peer)
            continue
        if global_count >= MAIN_COUNT:
            with open('tmp_data.json', 'w') as f:
                json.dump(tmp_data, f)
            return True

    return False


def give_reward():
    with open('tmp_data.json', 'r') as f:
        data = json.load(f)
        for i in data:
            print(i)
            device = data[i]['device_name']
            d = {'device_name': device, 'count': 2}
            reply = requests.post(LIC_IP + 'update_count', json=d)


def take_penalty():
    all_devices = []
    real_device = []
    with open('tmp_data.json', 'r') as f:
        data = json.load(f)
    for i in data:
        real_device.append(data[i]['device_name'])
    reply = requests.get(LIC_IP + 'get_device_name')
    js_data = reply.json()
    for i in js_data:
        all_devices.append(js_data[i])
    result = list(set(all_devices) - set(real_device))
    print(result)
    for i in range(len(result)):
        data = {'device_name': result[i], 'count': -2}
        reply = requests.post(LIC_IP + '/update_count', json=data)





def validate_possible_block(possible_block_dict):
    possible_block = Block(possible_block_dict)
    if possible_block.is_valid():
        possible_block.self_save()

        # we want to kill and restart the mining block so it knows it lost
        sched.print_jobs()
        try:
            sched.remove_job('mining')
            print("removed running mine job in validating possible block")
        except apscheduler.jobstores.base.JobLookupError:
            print("mining job didn't exist when validating possible block")

        print("readding mine for block validating_possible_block")
        print(sched)
        print(sched.get_jobs())
        sched.add_job(mine_for_block, kwargs={'rounds': STANDARD_ROUNDS, 'start_nonce': 0},
                      id='mining')  # add the block again
        print(sched.get_jobs())

        return True
    return False


def check_hash(hash):
    if str(hash[0:NUM_ZEROS]) == '0' * NUM_ZEROS:
        return True


if __name__ == '__main__':
    sched.add_job(mine_for_block, kwargs={'rounds': STANDARD_ROUNDS, 'start_nonce': 0},
                  id='mining')  # add the block again
    sched.add_listener(mine_for_block_listener, apscheduler.events.EVENT_JOB_EXECUTED)
    sched.start()
