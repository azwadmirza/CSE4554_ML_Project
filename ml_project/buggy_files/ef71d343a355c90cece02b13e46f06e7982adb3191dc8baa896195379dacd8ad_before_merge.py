def main():
    argument_spec = ec2_argument_spec()
    argument_spec.update(
        dict(
            role_arn=dict(required=True, default=None),
            role_session_name=dict(required=True, default=None),
            duration_seconds=dict(required=False, default=None, type='int'),
            external_id=dict(required=False, default=None),
            policy=dict(required=False, default=None),
            mfa_serial_number=dict(required=False, default=None),
            mfa_token=dict(required=False, default=None)
        )
    )

    module = AnsibleModule(argument_spec=argument_spec)

    if not HAS_BOTO:
        module.fail_json(msg='boto required for this module')

    region, ec2_url, aws_connect_params = get_aws_connection_info(module)

    if region:
        try:
            connection = connect_to_aws(boto.sts, region, **aws_connect_params)
        except (boto.exception.NoAuthHandlerFound, AnsibleAWSError) as e:
            module.fail_json(msg=str(e))
    else:
        module.fail_json(msg="region must be specified")

    try:
        assume_role_policy(connection, module)
    except BotoServerError as e:
        module.fail_json(msg=e)