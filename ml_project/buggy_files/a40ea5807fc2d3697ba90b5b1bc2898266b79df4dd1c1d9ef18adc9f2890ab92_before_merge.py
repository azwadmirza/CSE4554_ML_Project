async def async_setup_entry(hass, config_entry, async_add_entities):
    """Set up PS4 from a config entry."""
    config = config_entry
    await async_setup_platform(hass, config, async_add_entities, discovery_info=None)