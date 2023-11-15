async def async_setup(hass, config):
    """Setup configured zones as well as home assistant zone if necessary."""
    hass.data[DOMAIN] = {}
    entities = set()
    zone_entries = configured_zones(hass)
    for _, entry in config_per_platform(config, DOMAIN):
        if slugify(entry[CONF_NAME]) not in zone_entries:
            zone = Zone(hass, entry[CONF_NAME], entry[CONF_LATITUDE],
                        entry[CONF_LONGITUDE], entry.get(CONF_RADIUS),
                        entry.get(CONF_ICON), entry.get(CONF_PASSIVE))
            zone.entity_id = async_generate_entity_id(
                ENTITY_ID_FORMAT, entry[CONF_NAME], entities)
            hass.async_add_job(zone.async_update_ha_state())
            entities.add(zone.entity_id)

    if ENTITY_ID_HOME not in entities and HOME_ZONE not in zone_entries:
        zone = Zone(hass, hass.config.location_name,
                    hass.config.latitude, hass.config.longitude,
                    DEFAULT_RADIUS, ICON_HOME, False)
        zone.entity_id = ENTITY_ID_HOME
        hass.async_add_job(zone.async_update_ha_state())

    return True