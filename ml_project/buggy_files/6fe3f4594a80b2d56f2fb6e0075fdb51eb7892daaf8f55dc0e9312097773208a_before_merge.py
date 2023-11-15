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