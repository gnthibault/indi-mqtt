#!/usr/bin/env python3
# coding=utf-8

"""
Copyright(c) 2019 Radek Kaczorek  <rkaczorek AT gmail DOT com>

This library is free software; you can redistribute it and/or
modify it under the terms of the GNU Library General Public
License version 3 as published by the Free Software Foundation.

This library is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
Library General Public License for more details.

You should have received a copy of the GNU Library General Public License
along with this library; see the file COPYING.LIB.  If not, write to
the Free Software Foundation, Inc., 51 Franklin Street, Fifth Floor,
Boston, MA 02110-1301, USA.
"""

import os, sys, time, logging, configparser
import argparse
from indi_mr import inditomqtt, indi_server, mqtt_server

__author__ = 'Radek Kaczorek'
__copyright__ = 'Copyright 2019-2020, Radek Kaczorek'
__license__ = 'GPL-3'
__version__ = '1.0.6'

# Default options
LOG_LEVEL = logging.INFO
LIST_TOPICS = False
CONFIG_FILE = "/etc/indi-mqtt.conf"

# INDI
INDI_HOST = 'localhost'
INDI_PORT = 7624

# MQTT
MQTT_HOST = 'localhost'
MQTT_PORT = 1883
MQTT_USER = None
MQTT_PASS = None
MQTT_ROOT = 'observatory'
MQTT_POLLING = 10
MQTT_JSON = False

# Init logging
logger = logging.getLogger('indi-mqtt')
logging.basicConfig(format='%(name)s: %(message)s', level=LOG_LEVEL, stream=sys.stdout)

parser = argparse.ArgumentParser()
parser.add_argument("-c", "--config", help="configuration file path (default = /etc/indi-mqtt.conf)")
parser.add_argument("--log_level", help="logging level (default = info)")
parser.add_argument("-l", "--list_topics", help="list available MQTT topics", action="store_true")
parser.add_argument("-j", "--mqtt_json", help="enable full json on MQTT root/json", action="store_true")
parser.add_argument("--indi_host", help="INDI server hostname or IP (default = localhost)")
parser.add_argument("--indi_port", help="INDI server port number (default = 7624)")
parser.add_argument("--mqtt_host", help="MQTT server hostname or IP (default = localhost)")
parser.add_argument("--mqtt_port", help="MQTT server port number (default = 1883)")
parser.add_argument("--mqtt_user", help="MQTT server username (default = none)")
parser.add_argument("--mqtt_pass", help="MQTT server password (default = none)")
parser.add_argument("--mqtt_root", help="MQTT root topic name (default = observatory)")
parser.add_argument("--mqtt_polling", help="MQTT polling time in seconds (default = 10)")
args = parser.parse_args()

if args.config:
	CONFIG_FILE = args.config

if os.path.isfile(CONFIG_FILE):
		config = configparser.ConfigParser()
		config.read(CONFIG_FILE)
		logger.info("Using configuration from " + CONFIG_FILE)

		if 'LOG_LEVEL' in config['DEFAULT']:
			if config['DEFAULT']['LOG_LEVEL'].lower() == 'info':
				LOG_LEVEL = logging.INFO
			if config['DEFAULT']['LOG_LEVEL'].lower() == 'debug':
				LOG_LEVEL = logging.DEBUG
			if config['DEFAULT']['LOG_LEVEL'].lower() == 'warning':
				LOG_LEVEL = logging.WARNING
			if config['DEFAULT']['LOG_LEVEL'].lower() == 'error':
				LOG_LEVEL = logging.ERROR
			if config['DEFAULT']['LOG_LEVEL'].lower() == 'critical':
				LOG_LEVEL = logging.CRITICAL
		if 'INDI_HOST' in config['INDI']:
			INDI_HOST = config['INDI']['INDI_HOST']
		if 'INDI_PORT' in config['INDI']:
			INDI_PORT = int(config['INDI']['INDI_PORT'])
		if 'MQTT_HOST' in config['MQTT']:
			MQTT_HOST = config['MQTT']['MQTT_HOST']
		if 'MQTT_PORT' in config['MQTT']:
			MQTT_PORT = int(config['MQTT']['MQTT_PORT'])
		if 'MQTT_USER' in config['MQTT']:
			MQTT_USER = config['MQTT']['MQTT_USER']
		if 'MQTT_PASS' in config['MQTT']:
			MQTT_PASS = config['MQTT']['MQTT_PASS']
		if 'MQTT_ROOT' in config['MQTT']:
			MQTT_ROOT = config['MQTT']['MQTT_ROOT']
		if 'MQTT_POLLING' in config['MQTT']:
			MQTT_POLLING = int(config['MQTT']['MQTT_POLLING'])
		if 'MQTT_JSON' in config['MQTT']:
			if config['MQTT']['MQTT_JSON'].lower() == 'true':
				MQTT_JSON = True

if args.log_level:
	if args.log_level.lower() == 'info':
		LOG_LEVEL = logging.INFO
	if args.log_level.lower() == 'debug':
		LOG_LEVEL = logging.DEBUG
	if args.log_level.lower() == 'warning':
		LOG_LEVEL = logging.WARNING
	if args.log_level.lower() == 'error':
		LOG_LEVEL = logging.ERROR
	if args.log_level.lower() == 'critical':
		LOG_LEVEL = logging.CRITICAL

if args.list_topics:
	LIST_TOPICS = True
if args.indi_host:
	INDI_HOST = args.indi_host
if args.indi_port:
	INDI_PORT = int(args.indi_port)
if args.mqtt_host:
	MQTT_HOST = args.mqtt_host
if args.mqtt_port:
	MQTT_PORT = int(args.mqtt_port)
if args.mqtt_user:
	MQTT_USER = args.mqtt_user
if args.mqtt_pass:
	MQTT_PASS = args.mqtt_pass
if args.mqtt_root:
	MQTT_ROOT = args.mqtt_root
if args.mqtt_polling:
	MQTT_POLLING = int(args.mqtt_polling)
if args.mqtt_json:
	MQTT_JSON = True

# Set logging level
logger.setLevel(LOG_LEVEL)

# if user/pass available prepare auth data
if MQTT_USER and MQTT_PASS:
	MQTT_AUTH = {'username': MQTT_USER, 'password': MQTT_PASS}
else:
	MQTT_AUTH = None

if __name__ == '__main__':

	# define the hosts/ports where servers are listenning, these functions return named tuples.
	indi_host = indi_server(host=INDI_HOST, port=INDI_PORT)
	mqtt_host = mqtt_server(host=MQTT_HOST, port=MQTT_PORT)

	# blocking call which runs the service, communicating between indiserver and mqtt
	inditomqtt(indi_host, 'indi_mr_server', mqtt_host)

