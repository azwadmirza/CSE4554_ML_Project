def main():
    arg_spec = dict(
        user=dict(required=True, aliases=['username', 'name']),
        password=dict(default=None, no_log=True),
        tags=dict(default=None),
        permissions=dict(default=list(), type='list'),
        vhost=dict(default='/'),
        configure_priv=dict(default='^$'),
        write_priv=dict(default='^$'),
        read_priv=dict(default='^$'),
        force=dict(default='no', type='bool'),
        state=dict(default='present', choices=['present', 'absent']),
        node=dict(default='rabbit'),
        update_password=dict(default='on_create', choices=['on_create', 'always'])
    )
    module = AnsibleModule(
        argument_spec=arg_spec,
        supports_check_mode=True
    )

    username = module.params['user']
    password = module.params['password']
    tags = module.params['tags']
    permissions = module.params['permissions']
    vhost = module.params['vhost']
    configure_priv = module.params['configure_priv']
    write_priv = module.params['write_priv']
    read_priv = module.params['read_priv']
    force = module.params['force']
    state = module.params['state']
    node = module.params['node']
    update_password = module.params['update_password']

    if permissions:
        vhosts = map(lambda permission: permission.get('vhost', '/'), permissions)
        if any(map(lambda count: count > 1, count(vhosts).values())):
            module.fail_json(msg="Error parsing permissions: You can't have two permission dicts for the same vhost")
        bulk_permissions = True
    else:
        perm = {
            'vhost': vhost,
            'configure_priv': configure_priv,
            'write_priv': write_priv,
            'read_priv': read_priv
        }
        permissions.append(perm)
        bulk_permissions = False

    rabbitmq_user = RabbitMqUser(module, username, password, tags, permissions,
                                 node, bulk_permissions=bulk_permissions)

    result = dict(changed=False, user=username, state=state)
    if rabbitmq_user.get():
        if state == 'absent':
            rabbitmq_user.delete()
            result['changed'] = True
        else:
            if force:
                rabbitmq_user.delete()
                rabbitmq_user.add()
                rabbitmq_user.get()
                result['changed'] = True
            elif update_password == 'always':
                if not rabbitmq_user.check_password():
                    rabbitmq_user.change_password()
                    result['changed'] = True

            if rabbitmq_user.has_tags_modifications():
                rabbitmq_user.set_tags()
                result['changed'] = True

            if rabbitmq_user.has_permissions_modifications():
                rabbitmq_user.set_permissions()
                result['changed'] = True
    elif state == 'present':
        rabbitmq_user.add()
        rabbitmq_user.set_tags()
        rabbitmq_user.set_permissions()
        result['changed'] = True

    module.exit_json(**result)