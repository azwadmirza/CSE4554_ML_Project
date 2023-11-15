def main():

    argument_spec = dict(
        name=dict(type='str', required=True),
        state=dict(type='str', default='present', choices=['present', 'absent', 'stopped', 'running', 'restarted',
                                                           'rebooted']),
        zone=dict(type='str'),
        blueprint_id=dict(type='str'),
        bundle_id=dict(type='str'),
        key_pair_name=dict(type='str'),
        user_data=dict(type='str', default=''),
        wait=dict(type='bool', default=True),
        wait_timeout=dict(default=300, type='int'),
    )

    module = AnsibleAWSModule(argument_spec=argument_spec,
                              required_if=[['state', 'present', ('zone', 'blueprint_id', 'bundle_id')]])

    client = module.client('lightsail')

    name = module.params.get('name')
    state = module.params.get('state')

    if state == 'present':
        create_instance(module, client, name)
    elif state == 'absent':
        delete_instance(module, client, name)
    elif state in ('running', 'stopped'):
        start_or_stop_instance(module, client, name, state)
    elif state in ('restarted', 'rebooted'):
        restart_instance(module, client, name)