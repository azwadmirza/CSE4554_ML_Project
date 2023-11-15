def assume_role_policy(connection, module):

    role_arn = module.params.get('role_arn')
    role_session_name = module.params.get('role_session_name')
    policy = module.params.get('policy')
    duration_seconds = module.params.get('duration_seconds')
    external_id = module.params.get('external_id')
    mfa_serial_number = module.params.get('mfa_serial_number')
    mfa_token = module.params.get('mfa_token')
    changed = False

    try:
        assumed_role = connection.assume_role(role_arn, role_session_name, policy, duration_seconds, external_id, mfa_serial_number, mfa_token)
        changed = True
    except BotoServerError as e:
        module.fail_json(msg=e)

    module.exit_json(changed=changed, sts_creds=assumed_role.credentials.__dict__, sts_user=assumed_role.user.__dict__)