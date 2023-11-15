def request_configuration(hass, config, login, setup_platform_callback):
    """Request configuration steps from the user using the configurator."""
    configurator = hass.components.configurator

    async def configuration_callback(callback_data):
        """Handle the submitted configuration."""
        hass.async_add_job(setup_platform_callback, hass, config,
                           login, callback_data)
    status = login.status
    email = login.email
    # Get Captcha
    if (status and 'captcha_image_url' in status and
            status['captcha_image_url'] is not None):
        config_id = configurator.request_config(
            "Alexa Media Player - Captcha - {}".format(email),
            configuration_callback,
            description=('Please enter the text for the captcha.'
                         ' Please enter anything if the image is missing.'
                         ),
            description_image=status['captcha_image_url'],
            submit_caption="Confirm",
            fields=[{'id': 'captcha', 'name': 'Captcha'}]
        )
    elif (status and 'securitycode_required' in status and
          status['securitycode_required']):  # Get 2FA code
        config_id = configurator.request_config(
            "Alexa Media Player - 2FA - {}".format(email),
            configuration_callback,
            description=('Please enter your Two-Factor Security code.'),
            submit_caption="Confirm",
            fields=[{'id': 'securitycode', 'name': 'Security Code'}]
        )
    elif (status and 'claimspicker_required' in status and
          status['claimspicker_required']):  # Get picker method
        options = status['claimspicker_message']
        if options:
            config_id = configurator.request_config(
                "Alexa Media Player - Verification Method - {}".format(email),
                configuration_callback,
                description=('Please select the verification method. '
                             '(e.g., sms or email).<br />{}').format(
                                 options
                             ),
                submit_caption="Confirm",
                fields=[{'id': 'claimsoption', 'name': 'Option'}]
            )
        else:
            configuration_callback({})
    elif (status and 'verificationcode_required' in status and
          status['verificationcode_required']):  # Get picker method
        config_id = configurator.request_config(
            "Alexa Media Player - Verification Code - {}".format(email),
            configuration_callback,
            description=('Please enter received verification code.'),
            submit_caption="Confirm",
            fields=[{'id': 'verificationcode', 'name': 'Verification Code'}]
        )
    else:  # Check login
        config_id = configurator.request_config(
            "Alexa Media Player - Begin - {}".format(email),
            configuration_callback,
            description=('Please hit confirm to begin login attempt.'),
            submit_caption="Confirm",
            fields=[]
        )
    hass.data[DATA_ALEXAMEDIA]['accounts'][email]['config'].append(config_id)
    if 'error_message' in status and status['error_message']:
        configurator.notify_errors(  # use sync to delay next pop
            config_id,
            status['error_message'])
    if len(hass.data[DATA_ALEXAMEDIA]['accounts'][email]['config']) > 1:
        configurator.async_request_done((hass.data[DATA_ALEXAMEDIA]
                                         ['accounts'][email]['config']).pop(0))