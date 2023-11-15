def datasource_exists(name, jboss_config, datasource_properties, recreate=False, profile=None):
    '''
    Ensures that a datasource with given properties exist on the jboss instance.
    If datasource doesn't exist, it is created, otherwise only the properties that are different will be updated.

    name
        Datasource property name
    jboss_config
        Dict with connection properties (see state description)
    datasource_properties
        Dict with datasource properties
    recreate : False
        If set to True and datasource exists it will be removed and created again. However, if there are deployments that depend on the datasource, it will not me possible to remove it.
    profile : None
        The profile name for this datasource (domain mode only)

    Example:

    .. code-block:: yaml

        sampleDS:
          jboss7.datasource_exists:
           - recreate: False
           - datasource_properties:
               driver-name: mysql
               connection-url: 'jdbc:mysql://localhost:3306/sampleDatabase'
               jndi-name: 'java:jboss/datasources/sampleDS'
               user-name: sampleuser
               password: secret
               min-pool-size: 3
               use-java-context: True
           - jboss_config: {{ pillar['jboss'] }}
           - profile: full-ha

    '''
    log.debug(" ======================== STATE: jboss7.datasource_exists (name: %s) ", name)
    ret = {'name': name,
           'result': True,
           'changes': {},
           'comment': ''}

    has_changed = False
    ds_current_properties = {}
    ds_result = __salt__['jboss7.read_datasource'](jboss_config=jboss_config, name=name, profile=profile)
    if ds_result['success']:
        ds_current_properties = ds_result['result']
        if recreate:
            remove_result = __salt__['jboss7.remove_datasource'](jboss_config=jboss_config, name=name, profile=profile)
            if remove_result['success']:
                ret['changes']['removed'] = name
            else:
                ret['result'] = False
                ret['comment'] = 'Could not remove datasource. Stdout: '+remove_result['stdout']
                return ret

            has_changed = True  # if we are here, we have already made a change

            create_result = __salt__['jboss7.create_datasource'](jboss_config=jboss_config, name=name, datasource_properties=datasource_properties, profile=profile)
            if create_result['success']:
                ret['changes']['created'] = name
            else:
                ret['result'] = False
                ret['comment'] = 'Could not create datasource. Stdout: '+create_result['stdout']
                return ret

            read_result = __salt__['jboss7.read_datasource'](jboss_config=jboss_config, name=name, profile=profile)
            if read_result['success']:
                ds_new_properties = read_result['result']
            else:
                ret['result'] = False
                ret['comment'] = 'Could not read datasource. Stdout: '+read_result['stdout']
                return ret

        else:
            update_result = __salt__['jboss7.update_datasource'](jboss_config=jboss_config, name=name, new_properties=datasource_properties, profile=profile)
            if not update_result['success']:
                ret['result'] = False
                ret['comment'] = 'Could not update datasource. '+update_result['comment']
                # some changes to the datasource may have already been made, therefore we don't quit here
            else:
                ret['comment'] = 'Datasource updated.'

            read_result = __salt__['jboss7.read_datasource'](jboss_config=jboss_config, name=name, profile=profile)
            ds_new_properties = read_result['result']
    else:
        if ds_result['err_code'] == 'JBAS014807':  # ok, resource not exists:
            create_result = __salt__['jboss7.create_datasource'](jboss_config=jboss_config, name=name, datasource_properties=datasource_properties, profile=profile)
            if create_result['success']:
                read_result = __salt__['jboss7.read_datasource'](jboss_config=jboss_config, name=name, profile=profile)
                ds_new_properties = read_result['result']
                ret['comment'] = 'Datasource created.'
            else:
                ret['result'] = False
                ret['comment'] = 'Could not create datasource. Stdout: '+create_result['stdout']
        else:
            raise CommandExecutionError('Unable to handle error: {0}'.format(ds_result['failure-description']))

    if ret['result']:
        log.debug("ds_new_properties=%s", ds_new_properties)
        log.debug("ds_current_properties=%s", ds_current_properties)
        diff = dictdiffer.diff(ds_new_properties, ds_current_properties)

        added = diff.added()
        if len(added) > 0:
            has_changed = True
            ret['changes']['added'] = __format_ds_changes(added, ds_current_properties, ds_new_properties)

        removed = diff.removed()
        if len(removed) > 0:
            has_changed = True
            ret['changes']['removed'] = __format_ds_changes(removed, ds_current_properties, ds_new_properties)

        changed = diff.changed()
        if len(changed) > 0:
            has_changed = True
            ret['changes']['changed'] = __format_ds_changes(changed, ds_current_properties, ds_new_properties)

        if not has_changed:
            ret['comment'] = 'Datasource not changed.'

    return ret