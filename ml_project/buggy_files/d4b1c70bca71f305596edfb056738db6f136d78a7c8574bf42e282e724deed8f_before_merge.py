    def _fill_device_lists():
        for dev in devices.values():
            if isinstance(dev, SmartPlug):
                if dev.is_dimmable:  # Dimmers act as lights
                    lights.append(dev)
                else:
                    switches.append(dev)
            elif isinstance(dev, SmartBulb):
                lights.append(dev)
            else:
                _LOGGER.error("Unknown smart device type: %s", type(dev))