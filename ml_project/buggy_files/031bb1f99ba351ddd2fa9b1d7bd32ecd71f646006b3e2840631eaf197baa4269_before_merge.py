def setup(hass, config, discovery_info=None):
    """Set up the Alexa domain."""
    if DATA_ALEXAMEDIA not in hass.data:
        hass.data[DATA_ALEXAMEDIA] = {}
        hass.data[DATA_ALEXAMEDIA]['accounts'] = {}
    from alexapy import AlexaLogin

    config = config.get(DOMAIN)
    for account in config[CONF_ACCOUNTS]:
        # if account[CONF_EMAIL] in configured_instances(hass):
        #     continue

        email = account.get(CONF_EMAIL)
        password = account.get(CONF_PASSWORD)
        url = account.get(CONF_URL)
        hass.data[DOMAIN]['accounts'][email] = {"config": []}
        login = AlexaLogin(url, email, password, hass.config.path,
                           account.get(CONF_DEBUG))

        test_login_status(hass, account, login,
                          setup_platform_callback)
    return True