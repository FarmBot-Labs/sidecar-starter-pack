"""
Information class.
"""

# └── functions/information
#     ├── [API] get_info()
#     ├── [API] set_info()
#     ├── [API] safe_z()
#     ├── [API] garden_size()
#     ├── [API] group()
#     ├── [API] curve()
#     ├── [BROKER] soil_height()
#     ├── [BROKER] read_status()
#     └── [BROKER] read_sensor()

from .imports import *
from .broker import BrokerConnect
from .authentication import Authentication

class Information():
    def __init__(self, state):
        self.broker = BrokerConnect(state)
        self.auth = Authentication(state)

    def get_info(self, endpoint, id=None):
        # Get endpoint info
        endpoint_data = self.auth.request('GET', endpoint, id)
        # Return endpoint info as json object: endpoint[""]
        return endpoint_data

    def set_info(self, endpoint, field, value, id=None):
        # Edit endpoint info
        new_value = {
            field: value
        }
        self.auth.request('PATCH', endpoint, id, new_value)

        # Return endpoint info as json object: endpoint[""]
        new_endpoint_data = self.auth.request('GET', endpoint, id)
        return new_endpoint_data

    def safe_z(self):
        # Get safe z height via get_info()
        config_data = self.get_info('fbos_config')
        z_value = config_data["safe_height"]
        # Return safe z height as value
        return z_value

    def garden_size(self):
        # Get garden size parameters via get_info()
        json_data = self.get_info('firmware_config')

        x_steps = json_data['movement_axis_nr_steps_x']
        x_mm = json_data['movement_step_per_mm_x']

        y_steps = json_data['movement_axis_nr_steps_y']
        y_mm = json_data['movement_step_per_mm_y']

        length_x = x_steps / x_mm
        length_y = y_steps / y_mm
        area = length_x * length_y

        # Return garden size parameters as values
        return length_x, length_y, area

    def group(self, id=None):
        # Get all groups or single by id
        if id is None:
            group_data = self.get_info("point_groups")
        else:
            group_data = self.get_info('point_groups', id)

        # Return group as json object: group[""]
        return group_data

    def curve(self, id=None):
        # Get all curves or single by id
        if id is None:
            curve_data = self.get_info("curves")
        else:
            curve_data = self.get_info('curves', id)

        # Return curve as json object: curve[""]
        return curve_data

    def soil_height(self):
        # Execute soil height scripts
        # Return soil height as value
        soil_height_message = {
            **RPC_REQUEST,
            "body": [{
                "kind": "execute_script",
                "args": {
                    "label": "Measure Soil Height"
                }
            }]
        }

        self.broker.publish(soil_height_message)

    def read_status(self):
        # Get device status tree
        status_message = {
            "kind": "rpc_request",
            "args": {
                "label": "",
                "priority": 600
            },
            "body": [{
                    "kind": "read_status",
                    "args": {}
            }]
        }

        self.broker.publish(status_message)
        self.broker.listen(5, "status")

        status_tree = self.broker.state.last_message

        # Return status as json object: status[""]
        return status_tree

    def read_sensor(self, id):
        # Get sensor data
        peripheral_str = self.get_info("peripherals", id)
        mode = peripheral_str["mode"]

        sensor_message = {
            **RPC_REQUEST,
            "body": [{
                "kind": "read_pin",
                "args": {
                    "pin_mode": mode,
                    "label": "---",
                    "pin_number": {
                        "kind": "named_pin",
                        "args": {
                            "pin_type": "Peripheral",
                            "pin_id": id
                        }
                    }
                }
            }]
        }

        self.broker.publish(sensor_message)
        # Return sensor as json object: sensor[""]
