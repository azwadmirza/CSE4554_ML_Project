    def light_update(event):
        """ Callback for light updates from the RFXtrx gateway. """
        if not isinstance(event.device, rfxtrxmod.LightingDevice):
            return

        # Add entity if not exist and the automatic_add is True
        entity_id = slugify(event.device.id_string.lower())
        if entity_id not in rfxtrx.RFX_DEVICES:
            automatic_add = config.get('automatic_add', False)
            if not automatic_add:
                return

            _LOGGER.info(
                "Automatic add %s rfxtrx.light (Class: %s Sub: %s)",
                entity_id,
                event.device.__class__.__name__,
                event.device.subtype
            )
            pkt_id = "".join("{0:02x}".format(x) for x in event.data)
            entity_name = "%s : %s" % (entity_id, pkt_id)
            datas = {ATTR_STATE: False, ATTR_FIREEVENT: False}
            new_light = RfxtrxLight(entity_name, event, datas)
            rfxtrx.RFX_DEVICES[entity_id] = new_light
            add_devices_callback([new_light])

        # Check if entity exists or previously added automatically
        if entity_id in rfxtrx.RFX_DEVICES \
                and isinstance(rfxtrx.RFX_DEVICES[entity_id], RfxtrxLight):
            _LOGGER.debug(
                "EntityID: %s light_update. Command: %s",
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