"""
BasicCommands class.
"""

# └── functions/basic_commands.py
#     ├── [BROKER] wait()
#     ├── [BROKER] e_stop()
#     ├── [BROKER] unlock()
#     ├── [BROKER] reboot()
#     └── [BROKER] shutdown()

from .broker import BrokerConnect

class BasicCommands():
    """Basic commands class."""
    def __init__(self, state):
        self.broker = BrokerConnect(state)

    def wait(self, duration):
        """Pauses execution for a certain number of milliseconds."""

        self.broker.state.print_status(description=f"Waiting for {duration} milliseconds...")

        wait_message = {
            "kind": "wait",
            "args": {
                "milliseconds": duration
            }
        }

        self.broker.publish(wait_message)

    def e_stop(self):
        """Emergency locks (E-stops) the Farmduino microcontroller."""

        self.broker.state.print_status(description="Triggered device emergency stop")

        stop_message = {
            "kind": "emergency_lock",
            "args": {}
        }

        stop_message = self.broker.wrap_message(stop_message, priority=9000)
        self.broker.publish(stop_message)

    def unlock(self):
        """Unlocks a locked (E-stopped) device."""

        self.broker.state.print_status(description="Triggered device unlock")

        unlock_message = {
            "kind": "emergency_unlock",
            "args": {}
        }

        unlock_message = self.broker.wrap_message(unlock_message, priority=9000)
        self.broker.publish(unlock_message)

    def reboot(self):
        """Reboots the FarmBot OS and re-initializes the device."""

        self.broker.state.print_status(description="Triggered device reboot")

        reboot_message = {
            "kind": "reboot",
            "args": {
                "package": "farmbot_os"
            }
        }

        self.broker.publish(reboot_message)

    def shutdown(self):
        """Shuts down the FarmBot OS and turns the device off."""

        self.broker.state.print_status(description="Triggered device shutdown")

        shutdown_message = {
            "kind": "power_off",
            "args": {}
        }

        self.broker.publish(shutdown_message)
