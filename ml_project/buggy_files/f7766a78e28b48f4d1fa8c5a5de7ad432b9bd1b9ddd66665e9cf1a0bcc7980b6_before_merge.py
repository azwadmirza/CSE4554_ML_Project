def setup_platform(hass, config, add_devices_callback, discovery_info=None):
    """ Setup the RFXtrx platform. """
    import RFXtrx as rfxtrxmod

    # Add switch from config file
    switchs = []
    devices = config.get('devices')
    if devices:
        for entity_id, entity_info in devices.items():
            if entity_id not in rfxtrx.RFX_DEVICES:
                _LOGGER.info("Add %s rfxtrx.switch", entity_info[ATTR_NAME])

                # Check if i must fire event
                fire_event = entity_info.get(ATTR_FIREEVENT, False)
                datas = {ATTR_STATE: False, ATTR_FIREEVENT: fire_event}

                rfxobject = rfxtrx.get_rfx_object(entity_info[ATTR_PACKETID])
                newswitch = RfxtrxSwitch(
                    entity_info[ATTR_NAME], rfxobject, datas)
                rfxtrx.RFX_DEVICES[entity_id] = newswitch
                switchs.append(newswitch)

    add_devices_callback(switchs)

    def switch_update(event):
        """ Callback for sensor updates from the RFXtrx gateway. """
        if not isinstance(event.device, rfxtrxmod.LightingDevice):
            return

        # Add entity if not exist and the automatic_add is True
        entity_id = slugify(event.device.id_string.lower())
        if entity_id not in rfxtrx.RFX_DEVICES:
            automatic_add = config.get('automatic_add', False)
            if not automatic_add:
                return

            _LOGGER.info(
                "Automatic add %s rfxtrx.switch (Class: %s Sub: %s)",
                entity_id,
                event.device.__class__.__name__,
                event.device.subtype
            )
            pkt_id = "".join("{0:02x}".format(x) for x in event.data)
            entity_name = "%s : %s" % (entity_id, pkt_id)
            datas = {ATTR_STATE: False, ATTR_FIREEVENT: False}
            new_switch = RfxtrxSwitch(entity_name, event, datas)
            rfxtrx.RFX_DEVICES[entity_id] = new_switch
            add_devices_callback([new_switch])

        # Check if entity exists or previously added automatically
        if entity_id in rfxtrx.RFX_DEVICES \
                and isinstance(rfxtrx.RFX_DEVICES[entity_id], RfxtrxSwitch):
            _LOGGER.debug(
                "EntityID: %s switch_update. Command: %s",
                entity_id,
                event.values['Command']
            )
            if event.values['Command'] == 'On'\
                    or event.values['Command'] == 'Off':

                # Update the rfxtrx device state
                is_on = event.values['Command'] == 'On'
                # pylint: disable=protected-access
                rfxtrx.RFX_DEVICES[entity_id]._state = is_on
                rfxtrx.RFX_DEVICES[entity_id].update_ha_state()

                # Fire event
                if rfxtrx.RFX_DEVICES[entity_id].should_fire_event:
                    rfxtrx.RFX_DEVICES[entity_id].hass.bus.fire(
                        EVENT_BUTTON_PRESSED, {
                            ATTR_ENTITY_ID:
                                rfxtrx.RFX_DEVICES[entity_id].entity_id,
                            ATTR_STATE: event.values['Command'].lower()
                        }
                    )

    # Subscribe to main rfxtrx events
    if switch_update not in rfxtrx.RECEIVED_EVT_SUBSCRIBERS:
        rfxtrx.RECEIVED_EVT_SUBSCRIBERS.append(switch_update)