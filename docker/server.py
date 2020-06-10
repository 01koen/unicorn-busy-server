#!/usr/bin/env python

import json
from datetime import datetime
import paho.mqtt.client as mqtt

from flask import Flask, jsonify, make_response, request
from random import randint

globalRed = 0
globalGreen = 0
globalBlue = 0
globalLastCalled = None
globalLastCalledApi = None

app = Flask(__name__)

def setTimestamp() :
	global globalLastCalled
	globalLastCalled = datetime.now()

def switchOn() :
	red = randint(10, 255)
	green = randint(10, 255)
	blue = randint(10, 255)
	client = mqtt.Client()
	client.connect("192.168.1.100",1883,60)
	client.publish("cmnd/tasmota_D9264E/Dimmer", '35')
	client.disconnect()
	publish(red,green,blue)

def switchOff() :
	global  globalBlue, globalGreen, globalRed
	globalRed = 0
	globalGreen = 0
	globalBlue = 0
	client = mqtt.Client()
	client.connect("192.168.1.100",1883,60)
	client.publish("cmnd/tasmota_D9264E/POWER", 'OFF')
	client.disconnect()

def publish(red,green,blue) :
	payload = str(red) + ',' + str(green) + ',' + str(blue)
	client = mqtt.Client()
	client.connect("192.168.1.100",1883,60)
	client.publish("cmnd/tasmota_D9264E/Color2", payload)
	client.disconnect()

# API Initialization
@app.route('/api/on', methods=['GET'])
def apiOn() :
	global globalLastCalledApi
	globalLastCalledApi = '/api/on'
	content = request.json
	print(content)
	switchOff()
	switchOn()
	setTimestamp()
	return jsonify({})

@app.route('/api/off', methods=['GET'])
def apiOff() :
	global crntColors, globalLastCalledApi
	globalLastCalledApi = '/api/off'
	crntColors = None
	content = request.json
	print(content)
	switchOff()
	setTimestamp()
	return jsonify({})

@app.route('/api/switch', methods=['POST'])
def apiSwitch() :
	global globalLastCalledApi
	globalLastCalledApi = '/api/switch'
	switchOff()
	content = request.json
	print(content)
	red = content.get('red', '')
	green = content.get('green', '')
	blue = content.get('blue', '')
	setTimestamp()
	publish(red,green,blue)
	return make_response(jsonify())

@app.route('/api/status', methods=['GET'])
def apiStatus() :
	global globalBlue, globalGreen, globalRed, globalLastCalled, globalLastCalledApi
	return jsonify({ 'red': globalRed, 'green': globalGreen, 'blue': globalBlue, 'lastCalled': globalLastCalled, 'lastCalledApi': globalLastCalledApi })

@app.errorhandler(404)
def not_found(error):
	return make_response(jsonify({'error': 'Not found'}), 404)

if __name__ == '__main__':
	app.run(host='0.0.0.0', debug=False)
