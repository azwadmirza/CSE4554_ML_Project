    def get_optics(self):
        command = "show interfaces transceiver"
        output = self._send_command(command)

        # Check if router supports the command
        if "% Invalid input" in output:
            return {}

        # Formatting data into return data structure
        optics_detail = {}

        try:
            split_output = re.split(r"^---------.*$", output, flags=re.M)[1]
        except IndexError:
            return {}

        split_output = split_output.strip()

        for optics_entry in split_output.splitlines():
            # Example, Te1/0/1      34.6       3.29      -2.0      -3.5
            try:
                split_list = optics_entry.split()
            except ValueError:
                return {}

            int_brief = split_list[0]
            output_power = split_list[3]
            input_power = split_list[4]

            port = canonical_interface_name(int_brief)

            port_detail = {"physical_channels": {"channel": []}}

            # If interface is shutdown it returns "N/A" as output power.
            # Converting that to -100.0 float
            try:
                float(output_power)
            except ValueError:
                output_power = -100.0

            # Defaulting avg, min, max values to -100.0 since device does not
            # return these values
            optic_states = {
                "index": 0,
                "state": {
                    "input_power": {
                        "instant": (float(input_power) if "input_power" else -100.0),
                        "avg": -100.0,
                        "min": -100.0,
                        "max": -100.0,
                    },
                    "output_power": {
                        "instant": (float(output_power) if "output_power" else -100.0),
                        "avg": -100.0,
                        "min": -100.0,
                        "max": -100.0,
                    },
                    "laser_bias_current": {
                        "instant": 0.0,
                        "avg": 0.0,
                        "min": 0.0,
                        "max": 0.0,
                    },
                },
            }

            port_detail["physical_channels"]["channel"].append(optic_states)
            optics_detail[port] = port_detail

        return optics_detail