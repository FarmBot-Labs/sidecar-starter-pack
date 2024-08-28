"""
Information class.
"""

# └── functions/information
#     ├── [API] get_info()
#     ├── [API] edit_info()
#     ├── [API] add_info()
#     ├── [API] safe_z()
#     ├── [API] garden_size()
#     ├── [API] group()
#     ├── [API] curve()
#     ├── [BROKER] soil_height()
#     ├── [BROKER] read_status()
#     └── [BROKER] read_sensor()

from .broker import BrokerConnect
from .authentication import Authentication

class Information():
    """Information class."""
    def __init__(self, state):
        self.broker = BrokerConnect(state)
        self.auth = Authentication(state)

    def get_info(self, endpoint, database_id=None):
        """Get information about a specific endpoint."""

        endpoint_data = self.auth.request("GET", endpoint, database_id)

        self.broker.state.print_status(endpoint_json=endpoint_data)
        return endpoint_data

    def edit_info(self, endpoint, new_data, database_id=None):
        """Change information contained within an endpoint."""

        self.auth.request("PATCH", endpoint, database_id=database_id, payload=new_data)
        endpoint_data = self.get_info(endpoint, database_id)

        self.broker.state.print_status(endpoint_json=endpoint_data)
        return endpoint_data

    def add_info(self, endpoint, new_data):
        """Create new information contained within an endpoint."""

        self.auth.request("POST", endpoint, database_id=None, payload=new_data)

        endpoint_data = self.get_info(endpoint, database_id=None)

        self.broker.state.print_status(endpoint_json=endpoint_data)
        return endpoint_data

    def safe_z(self):
        """Returns the highest safe point along the z-axis."""

        config_data = self.get_info('fbos_config')
        z_value = config_data["safe_height"]

        self.broker.state.print_status(description=f"Safe z={z_value}")
        return z_value

    def garden_size(self):
        """Returns x-axis length, y-axis length, and area of garden bed."""

        json_data = self.get_info('firmware_config')

        x_steps = json_data['movement_axis_nr_steps_x']
        x_mm = json_data['movement_step_per_mm_x']

        y_steps = json_data['movement_axis_nr_steps_y']
        y_mm = json_data['movement_step_per_mm_y']

        length_x = x_steps / x_mm
        length_y = y_steps / y_mm
        area = length_x * length_y

        self.broker.state.print_status(description=f"X-axis length={length_x}\n Y-axis length={length_y}\n Area={area}")
        return length_x, length_y, area

    def group(self, group_id=None):
        """Returns all group info or single by id."""

        if group_id is None:
            group_data = self.get_info("point_groups")
        else:
            group_data = self.get_info('point_groups', group_id)

        self.broker.state.print_status(endpoint_json=group_data)
        return group_data

    def curve(self, curve_id=None):
        """Returns all curve info or single by id."""

        if curve_id is None:
            curve_data = self.get_info("curves")
        else:
            curve_data = self.get_info('curves', curve_id)

        self.broker.state.print_status(endpoint_json=curve_data)
        return curve_data

    def soil_height(self):
        """Use the camera to determine soil height at the current location."""

        soil_height_message = {
            "kind": "execute_script",
            "args": {
                "label": "Measure Soil Height"
            }
        }

        self.broker.publish(soil_height_message)

    def read_status(self):
        """Returns the FarmBot status tree."""

        status_message = {
            "kind": "read_status",
            "args": {}
        }
        status_message = self.broker.wrap_message(status_message, priority=600)
        self.broker.publish(status_message)

        self.broker.listen(15, "status")

        status_tree = self.broker.state.last_message

        self.broker.state.print_status(endpoint_json=status_tree)
        return status_tree

    def read_sensor(self, peripheral_id):
        """Reads the given pin by id."""

        peripheral_str = self.get_info("peripherals", peripheral_id)
        mode = peripheral_str["mode"]

        sensor_message = {
            "kind": "read_pin",
            "args": {
                "pin_mode": mode,
                "label": "---",
                "pin_number": {
                    "kind": "named_pin",
                    "args": {
                        "pin_type": "Peripheral",
                        "pin_id": peripheral_id,
                    }
                }
            }
        }

        self.broker.publish(sensor_message)
