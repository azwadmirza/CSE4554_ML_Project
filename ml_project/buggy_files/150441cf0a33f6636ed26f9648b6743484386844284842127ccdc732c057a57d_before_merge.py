def map_obj_to_commands(want, have, module):
    """ Define ovs-vsctl command to meet desired state """
    commands = list()

    if module.params['state'] == 'absent':
        if 'key' in have.keys():
            templatized_command = "%(ovs-vsctl)s -t %(timeout)s remove %(table)s %(record)s " \
                                  "%(col)s %(key)s=%(value)s"
            commands.append(templatized_command % module.params)
        elif module.params['key'] is None:
            templatized_command = "%(ovs-vsctl)s -t %(timeout)s remove %(table)s %(record)s " \
                                  "%(col)s"
            commands.append(templatized_command % module.params)
    else:
        if module.params['key'] is None:
            templatized_command = "%(ovs-vsctl)s -t %(timeout)s set %(table)s %(record)s " \
                                  "%(col)s=%(value)s"
            commands.append(templatized_command % module.params)
        elif 'key' not in have.keys():
            templatized_command = "%(ovs-vsctl)s -t %(timeout)s add %(table)s %(record)s " \
                                  "%(col)s %(key)s=%(value)s"
            commands.append(templatized_command % module.params)
        elif want['value'] != have['value']:
            templatized_command = "%(ovs-vsctl)s -t %(timeout)s set %(table)s %(record)s " \
                                  "%(col)s:%(key)s=%(value)s"
            commands.append(templatized_command % module.params)

    return commands