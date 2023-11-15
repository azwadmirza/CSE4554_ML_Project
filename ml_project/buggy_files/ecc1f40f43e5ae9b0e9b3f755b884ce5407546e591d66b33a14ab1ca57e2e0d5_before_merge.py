def get_user_policy_data(boto3_session, user_list):
    resource_client = boto3_session.resource('iam')
    policies = {}
    for user in user_list:
        name = user["UserName"]
        arn = user["Arn"]
        resource_user = resource_client.User(name)
        policies[arn] = {p.name: p.policy_document["Statement"] for p in resource_user.policies.all()}
    return policies