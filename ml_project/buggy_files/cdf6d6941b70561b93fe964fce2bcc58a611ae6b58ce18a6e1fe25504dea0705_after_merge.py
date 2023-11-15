def _validate(template_body=None, template_url=None, region=None, key=None, keyid=None, profile=None):
    # Validates template. returns true if template syntax is correct.
    validate = __salt__['boto_cfn.validate_template'](template_body, template_url, region, key, keyid, profile)
    log.debug('Validate result is {0}.'.format(str(validate)))
    if isinstance(validate, str):
        code, message = _get_error(validate)
        log.debug('Validate error is {0} and message is {1}.'.format(code, message))
        return code, message
    return True