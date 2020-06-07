from flask import Flask, jsonify, request
import requests
import os
import json
import csv
import sys
import apscheduler
import argparse
import lic_utils
from config import *
import glob
from forms import IndexForm, ComForm
from flask import render_template, flash, redirect
from flask_bootstrap import Bootstrap
from templates import *

lic_node = Flask(__name__)
lic_node.config.from_object(Config)
bootstrap = Bootstrap(lic_node)


def mine_master_lic():
    st = 'password'
    node = lic_utils.generate_hash(st)
    first_block = lic_utils.create_new_block_from_prev(prev_block=None, node=node, count=100)
    first_block.update_self_hash()#calculate_hash(index, prev_hash, data, timestamp, nonce)
    while str(first_block.hash[0:NUM_ZEROS]) != '0' * NUM_ZEROS:
        first_block.nonce += 1
        first_block.update_self_hash()
    #assert first_block.is_valid()
    return first_block


if not os.path.exists(LIC_DIR):
    os.mkdir(LIC_DIR)


if os.listdir(LIC_DIR) == []:
    # create the first block
    first_block = mine_master_lic()
    first_block.self_save()
    # need a data.txt to tell which port we're running on
    filename = "%s/data.txt" % LIC_DIR
    with open(filename, 'w') as data_file:
        data_file.write('password')
else:
    print("Chaindata directory already has files. If you want to generate a first block, delete files and return")


@lic_node.route('/nodes', methods=['GET'])
def nodes():
    lic = lic_utils.get_nodes()  # update if they've changed
    json_blocks = json.dumps(lic.block_list_dict())
    return json_blocks


@lic_node.route('/add_node', methods=['GET', 'POST'])
def mined():
    form = IndexForm()
    #filename = '%snodes.json' % (LIC_DIR)
    if form.validate_on_submit():
        data = {'ip': form.ip.data, 'port':form.port.data, 'device_name': form.device_name.data, 'count': 0}
        lic_utils.mine_for_block(node=form.ip.data, device_name=form.device_name.data)
        if lic_utils.checker_json(form.device_name.data) != 1:
            lic_utils.add_to_json(data)
            flash('New node {} add'.format(form.ip.data))
            return redirect('/add_node')
        else:
            flash('Node {} already exist'.format(form.ip.data))
            return redirect('/add_node')
    return render_template('/index.html', titles='', form=form)


@lic_node.route('/add_command', methods=['GET', 'POST'])
def add():
    form = ComForm()
    #filename = '%snodes.json' % (LIC_DIR)
    if form.validate_on_submit():
        data = {'node': form.device_name.data, 'com': form.command.data}
        lic_utils.add_com_to_json(data)
        flash('New command for node {} add'.format(form.device_name.data))
        return redirect('/add_command')
    return render_template('/com.html', titles='', form=form)


@lic_node.route('/update_count', methods=['GET', 'POST'])
def upd_count():
    values = request.get_json()
    required = ['device_name', 'count']
    if not all(k in values for k in required):
        return 'Missing values', 400
    lic_utils.update_count(values['device_name'], values['count'])
    response = {'message': 'Count is changed'}
    return jsonify(response), 201


@lic_node.route('/give_command', methods=['GET'])
def give_com():
    with open('commands.json', 'r') as f:
        response = json.load(f)
    return jsonify(response), 201


@lic_node.route('/get_count', methods=['GET', 'POST'])
def get_count():
    values = request.get_json()
    required = ['device_name']
    if not all(k in values for k in required):
        return 'Missing values', 400
    response = {'message': lic_utils.get_count(values['device_name'])}
    return jsonify(response), 201


@lic_node.route('/get_peers', methods=['GET'])
def peers():
    peers = lic_utils.get_peers()
    return peers


@lic_node.route('/get_device_name', methods=['GET'])
def devices():
    devices = lic_utils.get_device_name()
    return devices


if __name__ == '__main__':
    filename = '%sdata.txt' % (LIC_DIR)
    with open(filename, 'w') as data_file:
        data_file.write("password")

    # now we know what port to use
    lic_node.run(host=DEVICE_IP, port=DEVICE_PORT)
