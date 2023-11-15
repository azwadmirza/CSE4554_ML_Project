def setup(hass, config):
    """ Setup the RFXtrx component. """

    # Declare the Handle event
    def handle_receive(event):
        """ Callback all subscribers for RFXtrx gateway. """

        # Log RFXCOM event
        entity_id = slugify(event.device.id_string.lower())
        packet_id = "".join("{0:02x}".format(x) for x in event.data)
        entity_name = "%s : %s" % (entity_id, packet_id)
        _LOGGER.info("Receive RFXCOM event from %s => %s",
                     event.device, entity_name)

        # Callback to HA registered components
        for subscriber in RECEIVED_EVT_SUBSCRIBERS:
            subscriber(event)

    # Try to load the RFXtrx module
    import RFXtrx as rfxtrxmod

    # Init the rfxtrx module
    global RFXOBJECT

    if ATTR_DEVICE not in config[DOMAIN]:
        _LOGGER.exception(
            "can found device parameter in %s YAML configuration section",
            DOMAIN
        )
        return False

    device = config[DOMAIN][ATTR_DEVICE]
    debug = config[DOMAIN].get(ATTR_DEBUG, False)

    RFXOBJECT = rfxtrxmod.Core(device, handle_receive, debug=debug)

    return True