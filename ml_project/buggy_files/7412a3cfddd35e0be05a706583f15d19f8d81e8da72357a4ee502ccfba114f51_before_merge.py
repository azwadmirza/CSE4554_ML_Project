def _device_info(path, props):
    name = props.get("Name", props.get("Alias", path.split("/")[-1]))
    address = props.get("Address", None)
    if address is None:
        try:
            address = path[-17:].replace("_", ":")
            if not validate_mac_address(address):
                address = None
        except Exception:
            address = None
    rssi = props.get("RSSI", "?")
    return name, address, rssi, path