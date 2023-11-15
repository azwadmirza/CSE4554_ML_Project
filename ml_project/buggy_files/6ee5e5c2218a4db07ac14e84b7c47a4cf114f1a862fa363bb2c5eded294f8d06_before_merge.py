    async def setup_platform_callback(hass, config_entry, login, callback_data):
        """Handle response from configurator.

        Args:
        callback_data (json): Returned data from configurator passed through
                            request_configuration and configuration_callback

        """
        _LOGGER.debug(
            (
                "Configurator closed for Status: %s\n"
                " got captcha: %s securitycode: %s"
                " Claimsoption: %s AuthSelectOption: %s "
                " VerificationCode: %s"
            ),
            login.status,
            callback_data.get("captcha"),
            callback_data.get("securitycode"),
            callback_data.get("claimsoption"),
            callback_data.get("authselectoption"),
            callback_data.get("verificationcode"),
        )
        await login.login(data=callback_data)
        await test_login_status(hass, config_entry, login, alexa_setup_callback)