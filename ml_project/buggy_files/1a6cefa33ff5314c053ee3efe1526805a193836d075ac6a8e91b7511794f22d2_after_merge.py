def main():
    argument_spec = influx.InfluxDb.influxdb_argument_spec()
    argument_spec.update(
        state=dict(default='present', type='str', choices=['present', 'absent']),
        user_name=dict(required=True, type='str'),
        user_password=dict(required=False, type='str', no_log=True),
        admin=dict(default='False', type='bool')
    )
    module = AnsibleModule(
        argument_spec=argument_spec,
        supports_check_mode=True
    )

    state = module.params['state']
    user_name = module.params['user_name']
    user_password = module.params['user_password']
    admin = module.params['admin']
    influxdb = influx.InfluxDb(module)
    client = influxdb.connect_to_influxdb()
    user = find_user(module, client, user_name)

    if state == 'present':
        if user:
            if user_password is None or check_user_password(module, client, user_name, user_password):
                module.exit_json(changed=False)
            else:
                set_user_password(module, client, user_name, user_password)
        else:
            user_password = user_password or ''
            create_user(module, client, user_name, user_password, admin)

    if state == 'absent':
        if user:
            drop_user(module, client, user_name)
        else:
            module.exit_json(changed=False)