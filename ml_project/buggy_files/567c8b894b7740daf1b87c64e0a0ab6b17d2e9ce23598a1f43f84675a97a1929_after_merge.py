async def async_setup(hass, config, discovery_info=None):
    # pylint: disable=unused-argument
    """Set up the Alexa domain."""
    if DOMAIN not in config:
        _LOGGER.debug(
            "Nothing to import from configuration.yaml, loading from Integrations",
        )
        return True

    domainconfig = config.get(DOMAIN)
    for account in domainconfig[CONF_ACCOUNTS]:
        entry_title = "{} - {}".format(account[CONF_EMAIL], account[CONF_URL])
        _LOGGER.debug(
            "Importing config information for %s - %s from configuration.yaml",
            hide_email(account[CONF_EMAIL]),
            account[CONF_URL],
        )
        if entry_title in configured_instances(hass):
            for entry in hass.config_entries.async_entries(DOMAIN):
                if entry_title == entry.title:
                    hass.config_entries.async_update_entry(
                        entry,
                        data={
                            CONF_EMAIL: account[CONF_EMAIL],
                            CONF_PASSWORD: account[CONF_PASSWORD],
                            CONF_URL: account[CONF_URL],
                            CONF_DEBUG: account[CONF_DEBUG],
                            CONF_INCLUDE_DEVICES: account[CONF_INCLUDE_DEVICES],
                            CONF_EXCLUDE_DEVICES: account[CONF_EXCLUDE_DEVICES],
                            CONF_SCAN_INTERVAL: account[
                                CONF_SCAN_INTERVAL
                            ].total_seconds(),
                        },
                    )
                    break
        else:
            hass.async_create_task(
                hass.config_entries.flow.async_init(
                    DOMAIN,
                    context={"source": SOURCE_IMPORT},
                    data={
                        CONF_EMAIL: account[CONF_EMAIL],
                        CONF_PASSWORD: account[CONF_PASSWORD],
                        CONF_URL: account[CONF_URL],
                        CONF_DEBUG: account[CONF_DEBUG],
                        CONF_INCLUDE_DEVICES: account[CONF_INCLUDE_DEVICES],
                        CONF_EXCLUDE_DEVICES: account[CONF_EXCLUDE_DEVICES],
                        CONF_SCAN_INTERVAL: account[CONF_SCAN_INTERVAL].total_seconds(),
                    },
                )
            )
    return True