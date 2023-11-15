async def async_setup(hass, config):
    """Setup configured zones as well as home assistant zone if necessary."""
    if DOMAIN not in hass.data:
        hass.data[DOMAIN] = {}
    zone_entries = configured_zones(hass)
    for _, entry in config_per_platform(config, DOMAIN):
        name = slugify(entry[CONF_NAME])
        if name not in zone_entries:
            zone = Zone(hass, entry[CONF_NAME], entry[CONF_LATITUDE],
                        entry[CONF_LONGITUDE], entry.get(CONF_RADIUS),
                        entry.get(CONF_ICON), entry.get(CONF_PASSIVE))
            zone.entity_id = async_generate_entity_id(
                ENTITY_ID_FORMAT, entry[CONF_NAME], None, hass)
            hass.async_add_job(zone.async_update_ha_state())
            hass.data[DOMAIN][name] = zone

    if HOME_ZONE not in hass.data[DOMAIN] and HOME_ZONE not in zone_entries:
        name = hass.config.location_name
        zone = Zone(hass, name, hass.config.latitude, hass.config.longitude,
                    DEFAULT_RADIUS, ICON_HOME, False)
        zone.entity_id = ENTITY_ID_HOME
        hass.async_add_job(zone.async_update_ha_state())
        hass.data[DOMAIN][slugify(name)] = zone

    return True