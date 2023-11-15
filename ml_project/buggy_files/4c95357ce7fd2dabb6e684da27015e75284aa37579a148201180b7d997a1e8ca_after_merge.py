def main():
    argument_spec = dict(
        name=dict(required=True),
        description=dict(required=False),
        organization=dict(required=False),
        notification_type=dict(required=True, choices=['email', 'slack', 'twilio', 'pagerduty', 'hipchat', 'webhook', 'irc']),
        notification_configuration=dict(required=False),
        username=dict(required=False),
        sender=dict(required=False),
        recipients=dict(required=False, type='list'),
        use_tls=dict(required=False, type='bool'),
        host=dict(required=False),
        use_ssl=dict(required=False, type='bool'),
        password=dict(required=False, no_log=True),
        port=dict(required=False, type='int'),
        channels=dict(required=False, type='list'),
        token=dict(required=False, no_log=True),
        account_token=dict(required=False, no_log=True),
        from_number=dict(required=False),
        to_numbers=dict(required=False, type='list'),
        account_sid=dict(required=False),
        subdomain=dict(required=False),
        service_key=dict(required=False, no_log=True),
        client_name=dict(required=False),
        message_from=dict(required=False),
        api_url=dict(required=False),
        color=dict(required=False, choices=['yellow', 'green', 'red', 'purple', 'gray', 'random']),
        rooms=dict(required=False, type='list'),
        notify=dict(required=False, type='bool'),
        url=dict(required=False),
        headers=dict(required=False, type='dict', default={}),
        server=dict(required=False),
        nickname=dict(required=False),
        targets=dict(required=False, type='list'),
        state=dict(choices=['present', 'absent'], default='present'),
    )

    module = TowerModule(argument_spec=argument_spec, supports_check_mode=True)

    name = module.params.get('name')
    description = module.params.get('description')
    organization = module.params.get('organization')
    notification_type = module.params.get('notification_type')
    notification_configuration = module.params.get('notification_configuration')
    username = module.params.get('username')
    sender = module.params.get('sender')
    recipients = module.params.get('recipients')
    use_tls = module.params.get('use_tls')
    host = module.params.get('host')
    use_ssl = module.params.get('use_ssl')
    password = module.params.get('password')
    port = module.params.get('port')
    channels = module.params.get('channels')
    token = module.params.get('token')
    account_token = module.params.get('account_token')
    from_number = module.params.get('from_number')
    to_numbers = module.params.get('to_numbers')
    account_sid = module.params.get('account_sid')
    subdomain = module.params.get('subdomain')
    service_key = module.params.get('service_key')
    client_name = module.params.get('client_name')
    message_from = module.params.get('message_from')
    api_url = module.params.get('api_url')
    color = module.params.get('color')
    rooms = module.params.get('rooms')
    notify = module.params.get('notify')
    url = module.params.get('url')
    headers = module.params.get('headers')
    server = module.params.get('server')
    nickname = module.params.get('nickname')
    targets = module.params.get('targets')
    state = module.params.get('state')

    json_output = {'notification': name, 'state': state}

    tower_auth = tower_auth_config(module)
    with settings.runtime_values(**tower_auth):
        tower_check_mode(module)
        notification_template = tower_cli.get_resource('notification_template')

        try:
            org_res = tower_cli.get_resource('organization')
            org = org_res.get(name=organization)

            if state == 'present':
                result = notification_template.modify(name=name, description=description, organization=org['id'],
                                                      notification_type=notification_type,
                                                      notification_configuration=notification_configuration,
                                                      username=username, sender=sender, recipients=recipients,
                                                      use_tls=use_tls, host=host, use_ssl=use_ssl, password=password,
                                                      port=port, channels=channels, token=token,
                                                      account_token=account_token, from_number=from_number,
                                                      to_numbers=to_numbers, account_sid=account_sid,
                                                      subdomain=subdomain, service_key=service_key,
                                                      client_name=client_name, message_from=message_from,
                                                      api_url=api_url, color=color, rooms=rooms, notify=notify,
                                                      url=url, headers=headers, server=server, nickname=nickname,
                                                      targets=targets, create_on_missing=True)
                json_output['id'] = result['id']
            elif state == 'absent':
                result = notification_template.delete(name=name)
        except (exc.NotFound) as excinfo:
            module.fail_json(msg='Failed to update notification template, organization not found: {0}'.format(excinfo), changed=False)
        except (exc.ConnectionError, exc.BadRequest, exc.AuthError) as excinfo:
            module.fail_json(msg='Failed to update notification template: {0}'.format(excinfo), changed=False)

    json_output['changed'] = result['changed']
    module.exit_json(**json_output)