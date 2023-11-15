def get_role_policy_data(boto3_session, role_list):
    resource_client = boto3_session.resource('iam')
    policies = {}
    for role in role_list:
        name = role["RoleName"]
        arn = role["Arn"]
        resource_role = resource_client.Role(name)
        policies[arn] = {p.name: p.policy_document["Statement"] for p in resource_role.policies.all()}
    return policies