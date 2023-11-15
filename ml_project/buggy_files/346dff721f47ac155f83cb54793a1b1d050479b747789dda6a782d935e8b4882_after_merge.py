def build_run_instance_spec(params, ec2=None):
    if ec2 is None:
        ec2 = module.client('ec2')

    spec = dict(
        ClientToken=uuid.uuid4().hex,
        MaxCount=1,
        MinCount=1,
    )
    # network parameters
    spec['NetworkInterfaces'] = build_network_spec(params, ec2)
    spec['BlockDeviceMappings'] = build_volume_spec(params)
    spec.update(**build_top_level_options(params))
    spec['TagSpecifications'] = build_instance_tags(params)

    # IAM profile
    if params.get('instance_role'):
        spec['IamInstanceProfile'] = dict(Arn=determine_iam_role(params.get('instance_role')))

    spec['InstanceType'] = params['instance_type']
    return spec