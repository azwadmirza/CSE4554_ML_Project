    def return_response(self, method, path, data, headers, response):
        req_data = None
        if method == 'POST' and path == '/':
            req_data = urlparse.parse_qs(to_str(data))
            action = req_data.get('Action')[0]

        if req_data:
            if action == 'DescribeStackResources':
                if response.status_code < 300:
                    response_dict = xmltodict.parse(response.content)['DescribeStackResourcesResponse']
                    resources = response_dict['DescribeStackResourcesResult']['StackResources']
                    if not resources:
                        # Check if stack exists
                        stack_name = req_data.get('StackName')[0]
                        cloudformation_client = aws_stack.connect_to_service('cloudformation')
                        try:
                            cloudformation_client.describe_stacks(StackName=stack_name)
                        except Exception:
                            return error_response('Stack with id %s does not exist' % stack_name, code=404)
            if action == 'DescribeStackResource':
                if response.status_code >= 500:
                    # fix an error in moto where it fails with 500 if the stack does not exist
                    return error_response('Stack resource does not exist', code=404)
            elif action == 'CreateStack' or action == 'UpdateStack':
                # run the actual deployment
                template = template_deployer.template_to_json(req_data.get('TemplateBody')[0])
                template_deployer.deploy_template(template, req_data.get('StackName')[0])
                if response.status_code >= 400:
                    return make_response(action)