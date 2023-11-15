def _catch_login_errors(func) -> Callable:
    """Detect AlexapyLoginError and attempt relogin."""
    import functools
    @functools.wraps(func)
    async def wrapper(*args, **kwargs) -> Any:
        try:
            result = await func(*args, **kwargs)
        except AlexapyLoginError as ex:  # pylint: disable=broad-except
            template = ("An exception of type {0} occurred."
                        " Arguments:\n{1!r}")
            message = template.format(type(ex).__name__, ex.args)
            _LOGGER.debug("%s.%s: detected bad login: %s",
                          func.__module__[func.__module__.find('.')+1:],
                          func.__name__,
                          message)
            instance = args[0]
            if hasattr(instance, '_login'):
                login = instance._login
                email = login.email
                hass = instance.hass if instance.hass else None
                if (hass and (
                    'configurator' not in (hass.data[DATA_ALEXAMEDIA]
                                           ['accounts'][email])
                    or not (hass.data[DATA_ALEXAMEDIA]['accounts'][email]
                        ['configurator']))):
                    config_entry = (
                        hass.data[DATA_ALEXAMEDIA]
                        ['accounts']
                        [email]
                        ['config_entry'])
                    callback = (
                        hass.data[DATA_ALEXAMEDIA]
                        ['accounts']
                        [email]
                        ['setup_platform_callback'])
                    test_login_status = (
                        hass.data[DATA_ALEXAMEDIA]
                        ['accounts']
                        [email]
                        ['test_login_status'])
                    _LOGGER.debug(
                        "%s: Alexa API disconnected; attempting to relogin",
                        hide_email(email))
                    await login.login_with_cookie()
                    await test_login_status(hass,
                                            config_entry, login,
                                            callback)
            return None
        return result
    return wrapper