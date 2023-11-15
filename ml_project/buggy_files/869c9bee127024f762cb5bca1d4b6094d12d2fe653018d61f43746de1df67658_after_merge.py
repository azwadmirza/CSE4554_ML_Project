async def async_setup_entry(hass, config_entry, async_add_devices):
    """Set up the Alexa media player platform by config_entry."""
    if await async_setup_platform(
        hass, config_entry.data, async_add_devices, discovery_info=None
    ):
        for component in DEPENDENT_ALEXA_COMPONENTS:
            if component == "notify":
                cleaned_config = config_entry.data.copy()
                cleaned_config.pop(CONF_PASSWORD, None)
                # CONF_PASSWORD contains sensitive info which is no longer needed
                hass.async_create_task(
                    async_load_platform(
                        hass,
                        component,
                        ALEXA_DOMAIN,
                        {CONF_NAME: ALEXA_DOMAIN, "config": cleaned_config},
                        cleaned_config,
                    )
                )
            else:
                hass.async_add_job(
                    hass.config_entries.async_forward_entry_setup(
                        config_entry, component
                    )
                )
        return True
    raise ConfigEntryNotReady