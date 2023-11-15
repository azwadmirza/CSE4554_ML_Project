async def add_devices(
    account: Text,
    devices: List[EntityComponent],
    add_devices_callback: Callable,
    include_filter: List[Text] = [],
    exclude_filter: List[Text] = [],
) -> bool:
    """Add devices using add_devices_callback."""
    new_devices = []
    for device in devices:
        if (
            include_filter
            and device.name not in include_filter
            or exclude_filter
            and device.name in exclude_filter
        ):
            _LOGGER.debug("%s: Excluding device: %s", account, device)
            continue
        new_devices.append(device)
    devices = new_devices
    if devices:
        _LOGGER.debug("%s: Adding %s", account, devices)
        try:
            add_devices_callback(devices, False)
            return True
        except HomeAssistantError as exception_:
            message = exception_.message  # type: str
            if message.startswith("Entity id already exists"):
                _LOGGER.debug("%s: Device already added: %s", account, message)
            else:
                _LOGGER.debug(
                    "%s: Unable to add devices: %s : %s", account, devices, message
                )
        except BaseException as ex:
            template = "An exception of type {0} occurred." " Arguments:\n{1!r}"
            message = template.format(type(ex).__name__, ex.args)
            _LOGGER.debug("%s: Unable to add devices: %s", account, message)
    else:
        return True
    return False