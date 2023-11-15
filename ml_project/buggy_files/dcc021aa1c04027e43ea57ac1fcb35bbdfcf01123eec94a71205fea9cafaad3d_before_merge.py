def bindings_exist(name, jboss_config, bindings, profile=None):
    '''
    Ensures that given JNDI binding are present on the server.
    If a binding doesn't exist on the server it will be created.
    If it already exists its value will be changed.

    jboss_config:
        Dict with connection properties (see state description)
    bindings:
        Dict with bindings to set.
    profile:
        The profile name (domain mode only)

    Example:

    .. code-block:: yaml

            jndi_entries_created:
              jboss7.bindings_exist:
               - bindings:
                  'java:global/sampleapp/environment': 'DEV'
                  'java:global/sampleapp/configurationFile': '/var/opt/sampleapp/config.properties'
               - jboss_config: {{ pillar['jboss'] }}

    '''
    log.debug(" ======================== STATE: jboss7.bindings_exist (name: %s) (profile: %s) ", name, profile)
    log.debug('bindings=%s', bindings)
    ret = {'name': name,
           'result': True,
           'changes': {},
           'comment': 'Bindings not changed.'}

    has_changed = False
    for key in bindings:
        value = six.text_type(bindings[key])
        query_result = __salt__['jboss7.read_simple_binding'](binding_name=key, jboss_config=jboss_config, profile=profile)
        if query_result['success']:
            current_value = query_result['result']['value']
            if current_value != value:
                update_result = __salt__['jboss7.update_simple_binding'](binding_name=key, value=value, jboss_config=jboss_config, profile=profile)
                if update_result['success']:
                    has_changed = True
                    __log_binding_change(ret['changes'], 'changed', key, value, current_value)
                else:
                    raise CommandExecutionError(update_result['failure-description'])
        else:
            if query_result['err_code'] == 'JBAS014807':  # ok, resource not exists:
                create_result = __salt__['jboss7.create_simple_binding'](binding_name=key, value=value, jboss_config=jboss_config, profile=profile)
                if create_result['success']:
                    has_changed = True
                    __log_binding_change(ret['changes'], 'added', key, value)
                else:
                    raise CommandExecutionError(create_result['failure-description'])
            else:
                raise CommandExecutionError(query_result['failure-description'])

    if has_changed:
        ret['comment'] = 'Bindings changed.'
    return ret