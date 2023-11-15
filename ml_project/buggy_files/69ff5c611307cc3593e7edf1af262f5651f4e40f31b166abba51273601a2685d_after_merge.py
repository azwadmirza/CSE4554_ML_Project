def assume_role_policy(connection, module):
    params = {
        'RoleArn': module.params.get('role_arn'),
        'RoleSessionName': module.params.get('role_session_name'),
        'Policy': module.params.get('policy'),
        'DurationSeconds': module.params.get('duration_seconds'),
        'ExternalId': module.params.get('external_id'),
        'SerialNumber': module.params.get('mfa_serial_number'),
        'TokenCode': module.params.get('mfa_token')
    }
    changed = False

    kwargs = dict((k, v) for k, v in params.items() if v is not None)

    try:
        response = connection.assume_role(**kwargs)
        changed = True
    except (ClientError, ParamValidationError) as e:
        module.fail_json_aws(e)

    sts_cred, sts_user = _parse_response(response)
    module.exit_json(changed=changed, sts_creds=sts_cred, sts_user=sts_user)