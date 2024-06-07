import sys
import json
import requests
from getpass import getpass # required for authorization token
import paho.mqtt.publish as publish # required for message broker

RPC_REQUEST = {
    "kind": "rpc_request",
    "args": {
        "label": ""
    }
}
class Farmbot():
    def __init__(self):
      self.token = None

    def get_token(self, EMAIL, PASSWORD, SERVER='https://my.farm.bot'):
        headers = {'content-type': 'application/json'}
        user = {'user': {'email': EMAIL, 'password': PASSWORD}}
        response = requests.post(f'{SERVER}/api/tokens', headers=headers, json=user)
        self.token = response.json()

    def publish_single(self, PAYLOAD):
        if self.token is None:
            print('Please call `get_token` first.')
            sys.exit(1)
        publish.single(
            f'bot/{self.token['token']['unencoded']['bot']}/from_clients',
            payload=json.dumps(PAYLOAD),
            hostname=self.token['token']['unencoded']['mqtt'],
            auth={
                'username': self.token['token']['unencoded']['bot'],
                'password': self.token['token']['encoded']
            }
        )

    def e_stop(self):
        e_stop_message = {
            **RPC_REQUEST,
            "body": [{
                "kind": "emergency_lock",
                "args": {}
            }]
        }

        self.publish_single(e_stop_message)

    def unlock(self):
        unlock_message = {
            **RPC_REQUEST,
            "body": [{
                "kind": "emergency_unlock",
                "args": {}
            }]
        }

        self.publish_single(unlock_message)

    def get_info(self, SOURCE, ID=''):
        url = f'https:{self.token['token']['unencoded']['iss']}/api/'+SOURCE+'/'+ID
        headers = {'authorization': self.token['token']['encoded'], 'content-type': 'application/json'}
        response = requests.get(url, headers=headers)
        return json.dumps(response.json(), indent=2)

    def edit_info(self, SOURCE, VALUE, CHANGE, ID=''):
        new_value = {
            VALUE: CHANGE
        }

        url = f'https:{self.token['token']['unencoded']['iss']}/api/'+SOURCE+'/'+ID
        headers = {'authorization': self.token['token']['encoded'], 'content-type': 'application/json'}
        response = requests.patch(url, headers=headers, data=json.dumps(new_value))
        return json.dumps(response.json(), indent=2)

    def new_log_API(MESSAGE, CHANNEL, TYPE, VERBOSITY):
        new_message = {
            'message': MESSAGE,
            'channel': [CHANNEL], # Doesn't currently do anything
            'type': TYPE,
            'verbosity': VERBOSITY
        }

        url = f'https:{self.token['token']['unencoded']['iss']}/api/logs'
        headers = {'authorization': self.token['token']['encoded'], 'content-type': 'application/json'}
        response = requests.post(url, headers=headers, data=json.dumps(new_message))
        return json.dumps(response.json(), indent=2)

    def new_log_BROKER(MESSAGE, TYPE):
        new_message = {
            **RPC_REQUEST,
            "body": [{
                'kind': 'send_message',
                'args': {
                    'message': MESSAGE,
                    'message_type': TYPE
                }
            }]
        }

        self.publish_single(new_message)

    def move_to(X, Y, Z):
        def axis_overwrite(AXIS, VALUE):
            return {
                "kind": "axis_overwrite",
                "args": {
                    "axis": AXIS,
                    "axis_operand": {
                        "kind": "numeric",
                        "args": {
                            "number": VALUE
                        }
                    }
                }
            }

        coordinates = {
            **RPC_REQUEST,
            "body": [{
                "kind": "move",
                "args": {},
                "body": [
                    axis_overwrite("x", X),
                    axis_overwrite("y", Y),
                    axis_overwrite("z", Z)
                ]
            }]
        }

        self.publish_single(coordinates)

    def control_peripheral(self, ID, VALUE, TYPE):
        control_message = {
            **RPC_REQUEST,
            "body": [{
                "kind": "write_pin",
                "args": {
                    "pin_value": VALUE, # Controls on/off or slider value
                    "pin_mode": TYPE, # Controls digital or analog
                    "pin_number": {
                        "kind": "named_pin",
                        "args": {
                            "pin_type": "Peripheral",
                            "pin_id": ID
                        }
                    }
                }
            }]
        }

        self.publish_single(control_message)
