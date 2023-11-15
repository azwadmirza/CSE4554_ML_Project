def determine_iam_role(name_or_arn, iam):
    if re.match(r'^arn:aws:iam::\d+:instance-profile/[\w+=/,.@-]+$', name_or_arn):
        return name_or_arn
    if iam is None:
        iam = module.client('iam')
    try:
        role = iam.get_instance_profile(InstanceProfileName=name_or_arn)
        return role['InstanceProfile']['Arn']
    except botocore.exceptions.ClientError as e:
        if e.response['Error']['Code'] == 'NoSuchEntity':
            module.fail_json_aws(e, msg="Could not find instance_role {0}".format(name_or_arn))
        module.fail_json_aws(e, msg="An error occurred while searching for instance_role {0}. Please try supplying the full ARN.".format(name_or_arn))