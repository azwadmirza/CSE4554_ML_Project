def main():

    argument_spec = rabbitmq_argument_spec()
    argument_spec.update(
        dict(
            state=dict(default='present', choices=['present', 'absent'], type='str'),
            name=dict(required=True, type='str'),
            durable=dict(default=True, type='bool'),
            auto_delete=dict(default=False, type='bool'),
            message_ttl=dict(default=None, type='int'),
            auto_expires=dict(default=None, type='int'),
            max_length=dict(default=None, type='int'),
            dead_letter_exchange=dict(default=None, type='str'),
            dead_letter_routing_key=dict(default=None, type='str'),
            arguments=dict(default=dict(), type='dict'),
            max_priority=dict(default=None, type='int')
        )
    )
    module = AnsibleModule(argument_spec=argument_spec, supports_check_mode=True)

    url = "%s://%s:%s/api/queues/%s/%s" % (
        module.params['login_protocol'],
        module.params['login_host'],
        module.params['login_port'],
        urllib_parse.quote(module.params['vhost'], ''),
        module.params['name']
    )

    if not HAS_REQUESTS:
        module.fail_json(msg="requests library is required for this module. To install, use `pip install requests`")

    result = dict(changed=False, name=module.params['name'])

    # Check if queue already exists
    r = requests.get(url, auth=(module.params['login_user'], module.params['login_password']),
                     verify=module.params['cacert'], cert=(module.params['cert'], module.params['key']))

    if r.status_code == 200:
        queue_exists = True
        response = r.json()
    elif r.status_code == 404:
        queue_exists = False
        response = r.text
    else:
        module.fail_json(
            msg="Invalid response from RESTAPI when trying to check if queue exists",
            details=r.text
        )

    if module.params['state'] == 'present':
        change_required = not queue_exists
    else:
        change_required = queue_exists

    # Check if attributes change on existing queue
    if not change_required and r.status_code == 200 and module.params['state'] == 'present':
        if not (
            response['durable'] == module.params['durable'] and
            response['auto_delete'] == module.params['auto_delete'] and
            (
                ('x-message-ttl' in response['arguments'] and response['arguments']['x-message-ttl'] == module.params['message_ttl']) or
                ('x-message-ttl' not in response['arguments'] and module.params['message_ttl'] is None)
            ) and
            (
                ('x-expires' in response['arguments'] and response['arguments']['x-expires'] == module.params['auto_expires']) or
                ('x-expires' not in response['arguments'] and module.params['auto_expires'] is None)
            ) and
            (
                ('x-max-length' in response['arguments'] and response['arguments']['x-max-length'] == module.params['max_length']) or
                ('x-max-length' not in response['arguments'] and module.params['max_length'] is None)
            ) and
            (
                ('x-dead-letter-exchange' in response['arguments'] and
                 response['arguments']['x-dead-letter-exchange'] == module.params['dead_letter_exchange']) or
                ('x-dead-letter-exchange' not in response['arguments'] and module.params['dead_letter_exchange'] is None)
            ) and
            (
                ('x-dead-letter-routing-key' in response['arguments'] and
                 response['arguments']['x-dead-letter-routing-key'] == module.params['dead_letter_routing_key']) or
                ('x-dead-letter-routing-key' not in response['arguments'] and module.params['dead_letter_routing_key'] is None)
            ) and
            (
                ('x-max-priority' in response['arguments'] and
                 response['arguments']['x-max-priority'] == module.params['max_priority']) or
                ('x-max-priority' not in response['arguments'] and module.params['max_priority'] is None)
            )
        ):
            module.fail_json(
                msg="RabbitMQ RESTAPI doesn't support attribute changes for existing queues",
            )

    # Copy parameters to arguments as used by RabbitMQ
    for k, v in {
        'message_ttl': 'x-message-ttl',
        'auto_expires': 'x-expires',
        'max_length': 'x-max-length',
        'dead_letter_exchange': 'x-dead-letter-exchange',
        'dead_letter_routing_key': 'x-dead-letter-routing-key',
        'max_priority': 'x-max-priority'
    }.items():
        if module.params[k] is not None:
            module.params['arguments'][v] = module.params[k]

    # Exit if check_mode
    if module.check_mode:
        result['changed'] = change_required
        result['details'] = response
        result['arguments'] = module.params['arguments']
        module.exit_json(**result)

    # Do changes
    if change_required:
        if module.params['state'] == 'present':
            r = requests.put(
                url,
                auth=(module.params['login_user'], module.params['login_password']),
                headers={"content-type": "application/json"},
                data=json.dumps({
                    "durable": module.params['durable'],
                    "auto_delete": module.params['auto_delete'],
                    "arguments": module.params['arguments']
                }),
                verify=module.params['cacert'],
                cert=(module.params['cert'], module.params['key'])
            )
        elif module.params['state'] == 'absent':
            r = requests.delete(url, auth=(module.params['login_user'], module.params['login_password']),
                                verify=module.params['cacert'], cert=(module.params['cert'], module.params['key']))

        # RabbitMQ 3.6.7 changed this response code from 204 to 201
        if r.status_code == 204 or r.status_code == 201:
            result['changed'] = True
            module.exit_json(**result)
        else:
            module.fail_json(
                msg="Error creating queue",
                status=r.status_code,
                details=r.text
            )

    else:
        module.exit_json(
            changed=False,
            name=module.params['name']
        )