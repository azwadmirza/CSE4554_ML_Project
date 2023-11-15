def update_cloudformation(method, path, data, headers, response=None, return_forward_info=False):
    req_data = None
    if method == 'POST' and path == '/':
        req_data = urlparse.parse_qs(data)
        action = req_data.get('Action')[0]

    if return_forward_info:
        if req_data:
            if action == 'CreateChangeSet':
                return create_change_set(req_data)
            elif action == 'DescribeChangeSet':
                return describe_change_set(req_data)
            elif action == 'ExecuteChangeSet':
                return execute_change_set(req_data)
        return True

    if req_data:
        if action == 'DescribeStackResources':
            response_dict = xmltodict.parse(response.content)['DescribeStackResourcesResponse']
            resources = response_dict['DescribeStackResourcesResult']['StackResources']
            if not resources:
                # TODO: check if stack exists
                return error_response('Stack does not exist', code=404)
        if action == 'DescribeStackResource':
            if response.status_code >= 500:
                # fix an error in moto where it fails with 500 if the stack does not exist
                return error_response('Stack resource does not exist', code=404)
        elif action == 'CreateStack' or action == 'UpdateStack':
            if response.status_code in range(200, 300):
                # run the actual deployment
                template = template_deployer.template_to_json(req_data.get('TemplateBody')[0])
                template_deployer.deploy_template(template)