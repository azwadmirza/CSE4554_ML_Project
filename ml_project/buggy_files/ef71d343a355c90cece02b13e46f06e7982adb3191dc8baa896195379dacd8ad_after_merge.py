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

    module = AnsibleAWSModule(argument_spec=argument_spec)

    region, ec2_url, aws_connect_kwargs = get_aws_connection_info(module, boto3=True)

    if region:
        connection = boto3_conn(module, conn_type='client', resource='sts',
                                region=region, endpoint=ec2_url, **aws_connect_kwargs)

    else:
        module.fail_json(msg="region must be specified")

    assume_role_policy(connection, module)