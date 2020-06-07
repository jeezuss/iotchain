from flask import Flask, jsonify, request
import requests
import json
import os
from forms import IndexForm
from flask import render_template, flash, redirect
from flask_bootstrap import Bootstrap
from config import DEVICE_NAME

data = Flask(__name__)
SECRET_KEY = 'testkey'
data.config['SECRET_KEY'] = SECRET_KEY
bootstrap = Bootstrap(data)

headers = {
  'Conten': 'application/json',
  'Authorization': 'Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiIxY2QwOGY2NjIwODM0NTk5YjFlNzZmZTdjZTA4MzU1NCIsImlhdCI6MTU5MDUyNTg2NiwiZXhwIjoxOTA1ODg1ODY2fQ.m271KEiFzAEULkMrKAg86prnGZqre2sIrkEP8EZUZMA'
}
def is_non_zero_file(fpath):
    return os.path.isfile(fpath) and os.path.getsize(fpath) > 0

@data.route('/send_data', methods=['GET', 'POST'])
def recive_command():
    values = request.get_json()
    print(values)
    print(type(values))
    required_com = ['command']
    required_rep = ['reply']
    if all(k in values for k in required_com):
        com = values['command']
        reply = requests.get(com, headers=headers)
        print(reply)
        reply_data = {'from': values['to'], 'to': values['from'], 'reply': reply.json()['state']}
        if os.path.exists('curr_commands.json'):
            with open('curr_commands.json', 'r') as f:
                js_data = json.load(f)
            with open('curr_commands.json', 'w') as f:
                index = len(js_data) + 1
                js_data.update({index: reply_data})
                json.dump(js_data, f)
        response = {'message': 'Command start'}
    elif all(k in values for k in required_rep):
        with open('curr_reply.json', 'r') as f:
            js_data = json.load(f)
        with open('curr_reply.json', 'w') as f:
            index = len(js_data) + 1
            js_data.update({index: values})
            json.dump(js_data, f)
            response = {'message': 'reply add'}
    return jsonify(response), 201

@data.route('/command', methods=['GET', 'POST'])
def command():
    form = IndexForm()
    if form.validate_on_submit():
        data = {'from': DEVICE_NAME,'to': form.device_name.data, 'command': form.command.data}
        flash('New command for node {} add'.format(form.device_name.data))
        if os.path.exists('curr_commands.json'):
            if is_non_zero_file('curr_comands.json') == True:
                with open('curr_commands.json', 'r') as f:
                    js_data = json.load(f)
            with open('curr_commands.json', 'w') as f:
                if is_non_zero_file('curr_comands.json') == False:
                    index = 1
                    js_data = {}
                    js_data.update({index: data})
                    json.dump(js_data, f)
                else:
                    index = len(js_data) + 1
                    js_data.update({index: data})
                    json.dump(js_data, f)
        return redirect('/command')
    return render_template('/index.html', titles='', form=form)


@data.route('/commands')
def commands():
    reply = requests.get('http://192.168.1.9:5001/give_command')
    with open('commands.json', 'w') as f:
        json.dump(reply.json(), f)
    js = reply.json()
    posts = []
    for row in js:
        #print(js[row])
        posts.append(js[row])
    return render_template('commands.html', posts=posts)

@data.route('/replyes')
def replyes():
    with open('curr_reply.json', 'r') as f:
        js_data = json.load(f)
    posts = []
    for row in js_data:
        #print(js[row])
        posts.append(js_data[row])
    return render_template('replyes.html', posts=posts)


if __name__ == '__main__':
    data.run(host='192.168.1.9', port=5010)