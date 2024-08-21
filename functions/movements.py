"""
MovementControls class.
"""

# └── functions/movements.py
#     ├── [BROKER] move()
#     ├── [BROKER] set_home()
#     ├── [BROKER] find_home()
#     ├── [BROKER] axis_length()
#     ├── [BROKER] get_xyz()
#     └── [BROKER] check_position()

from .imports import *
from .broker import BrokerConnect
from .information import Information

class MovementControls():
    def __init__(self, state):
        self.broker = BrokerConnect(state)
        self.info = Information(state)

    def move(self, x, y, z):
        """Moves to the specified (x, y, z) coordinate."""

        def axis_overwrite(axis, value):
            return {
                "kind": "axis_overwrite",
                "args": {
                    "axis": axis,
                    "axis_operand": {
                        "kind": "numeric",
                        "args": {
                            "number": value
                        }
                    }
                }
            }

        move_message = {
            "kind": "rpc_request",
            "args": {
                "label": "",
                "priority": 600
            },
            "body": [{
                "kind": "move",
                "args": {},
                "body": [
                    axis_overwrite("x", x),
                    axis_overwrite("y", y),
                    axis_overwrite("z", z)
                ]
            }]
        }

        self.broker.publish(move_message)
        return # TODO: return new xyz position as values

    def set_home(self, axis="all"):
        """Sets the current position as the home position for a specific axis."""

        set_home_message = {
            "kind": "rpc_request",
            "args": {
                "label": "",
                "priority": 600
            },
            "body": [{
                "kind": "zero",
                "args": {
                    "axis": axis
                }
            }]
        }

        self.broker.publish(set_home_message)
        return

    def find_home(self, axis="all", speed=100):
        """Moves the device to the home position for a specified axis."""

        if speed > 100 or speed < 1:
            return print("ERROR: Speed constrained to 1-100.")
        else:
            message = {
                "kind": "rpc_request",
                "args": {
                    "label": "",
                    "priority": 600
                },
                "body": [{
                    "kind": "find_home",
                    "args": {
                        "axis": axis,
                        "speed": speed
                    }
                }]
            }
            self.broker.publish(message)

        return # TODO: return new xyz position as values

    def axis_length(self, axis="all"):
        """Returns the length of a specified axis."""

        axis_length_message = {
            **RPC_REQUEST,
            "body": [{
                "kind": "calibrate",
                "args": {
                    "axis": axis
                }
            }]
        }

        self.broker.publish(axis_length_message)
        return # TODO: return axis length as values

    def get_xyz(self):
        """Returns the current (x, y, z) coordinates of the FarmBot."""

        tree_data = self.info.read_status()

        x_val = tree_data["location_data"]["position"]["x"]
        y_val = tree_data["location_data"]["position"]["y"]
        z_val = tree_data["location_data"]["position"]["z"]

        return x_val, y_val, z_val

    def check_position(self, user_x, user_y, user_z, tolerance):
        """Verifies position of the FarmBot within specified tolerance range."""

        user_values = [user_x, user_y, user_z]

        position = self.get_xyz()
        actual_vals = list(position)

        for user_value, actual_value in zip(user_values, actual_vals):
            if not actual_value - tolerance <= user_value <= actual_value + tolerance:
                print(f"Farmbot is NOT at position {position}")
                return False

        print(f"Farmbot is at position {position}")
        return True
