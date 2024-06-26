# farmbot_BROKER.py

import sys
import json

import paho.mqtt.publish as publish
import paho.mqtt.client as client

class FarmbotBroker():
    def __init__(self):
        self.token = None
        print("")

    def check_token(self):
        if self.token is None:
            print("ERROR: You have no token, please call `get_token` using your login credentials and the server you wish to connect to.")
            sys.exit(1)

    def publish(self, PAYLOAD):
        self.check_token()

        publish.single(
            f'bot/{self.token['token']['unencoded']['bot']}/from_clients',
            payload=json.dumps(PAYLOAD),
            hostname=self.token['token']['unencoded']['mqtt'],
            auth={
                'username': self.token['token']['unencoded']['bot'],
                'password': self.token['token']['encoded']
            }
        )
