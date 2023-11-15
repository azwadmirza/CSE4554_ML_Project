def apply_patches():
    """ Apply patches to make LocalStack seamlessly interact with the moto backend.
        TODO: Eventually, these patches should be contributed to the upstream repo! """

    # add model mappings to moto

    parsing.MODEL_MAP.update(MODEL_MAP)

    # Patch S3Backend.get_key method in moto to use S3 API from LocalStack

    def get_key(self, bucket_name, key_name, version_id=None):
        s3_client = aws_stack.connect_to_service('s3')
        value = b''
        if bucket_name != BUCKET_MARKER_LOCAL:
            value = s3_client.get_object(Bucket=bucket_name, Key=key_name)['Body'].read()
        return s3_models.FakeKey(name=key_name, value=value)

    s3_models.S3Backend.get_key = get_key

    # Patch clean_json in moto

    def clean_json(resource_json, resources_map):
        result = clean_json_orig(resource_json, resources_map)
        if isinstance(result, BaseModel):
            if isinstance(resource_json, dict) and 'Ref' in resource_json:
                entity_id = get_entity_id(result, resource_json)
                if entity_id:
                    return entity_id
                LOG.warning('Unable to resolve "Ref" attribute for: %s - %s - %s',
                            resource_json, result, type(result))
        return result

    clean_json_orig = parsing.clean_json
    parsing.clean_json = clean_json

    # Patch parse_and_create_resource method in moto to deploy resources in LocalStack

    def parse_and_create_resource(logical_id, resource_json, resources_map, region_name, force_create=False):
        try:
            return _parse_and_create_resource(logical_id, resource_json,
                resources_map, region_name, force_create=force_create)
        except Exception as e:
            LOG.error('Unable to parse and create resource "%s": %s %s' %
                      (logical_id, e, traceback.format_exc()))
            raise

    def parse_and_update_resource(logical_id, resource_json, resources_map, region_name):
        try:
            return _parse_and_create_resource(logical_id,
                resource_json, resources_map, region_name, update=True)
        except Exception as e:
            LOG.error('Unable to parse and update resource "%s": %s %s' %
                      (logical_id, e, traceback.format_exc()))
            raise

    def _parse_and_create_resource(logical_id, resource_json, resources_map, region_name,
            update=False, force_create=False):
        stack_name = resources_map.get('AWS::StackName')
        resource_hash_key = (stack_name, logical_id)

        # If the current stack is being updated, avoid infinite recursion
        updating = CURRENTLY_UPDATING_RESOURCES.get(resource_hash_key)
        LOG.debug('Currently processing stack resource %s/%s: %s' % (stack_name, logical_id, updating))
        if updating:
            return None

        # parse and get final resource JSON
        resource_tuple = parsing.parse_resource(logical_id, resource_json, resources_map)
        if not resource_tuple:
            return None
        _, resource_json, _ = resource_tuple

        # add some missing default props which otherwise cause deployments to fail
        props = resource_json['Properties'] = resource_json.get('Properties') or {}
        if resource_json['Type'] == 'AWS::Lambda::EventSourceMapping' and not props.get('StartingPosition'):
            props['StartingPosition'] = 'LATEST'

        # check if this resource already exists in the resource map
        resource = resources_map._parsed_resources.get(logical_id)
        if resource and not update and not force_create:
            return resource

        # check whether this resource needs to be deployed
        resource_map_new = dict(resources_map._resource_json_map)
        resource_map_new[logical_id] = resource_json
        should_be_created = template_deployer.should_be_deployed(logical_id, resource_map_new, stack_name)

        # fix resource ARNs, make sure to convert account IDs 000000000000 to 123456789012
        resource_json_arns_fixed = clone(json_safe(convert_objs_to_ids(resource_json)))
        set_moto_account_ids(resource_json_arns_fixed)

        # create resource definition and store CloudFormation metadata in moto
        if (resource or update) and not force_create:
            parse_and_update_resource_orig(logical_id,
                resource_json_arns_fixed, resources_map, region_name)
        elif not resource:
            try:
                resource = parse_and_create_resource_orig(logical_id,
                    resource_json_arns_fixed, resources_map, region_name)
            except Exception as e:
                if should_be_created:
                    raise
                else:
                    LOG.info('Error on moto CF resource creation. Ignoring, as should_be_created=%s: %s' %
                             (should_be_created, e))

        # Fix for moto which sometimes hard-codes region name as 'us-east-1'
        if hasattr(resource, 'region_name') and resource.region_name != region_name:
            LOG.debug('Updating incorrect region from %s to %s' % (resource.region_name, region_name))
            resource.region_name = region_name

        # check whether this resource needs to be deployed
        is_updateable = False
        if not should_be_created:
            # This resource is either not deployable or already exists. Check if it can be updated
            is_updateable = template_deployer.is_updateable(logical_id, resource_map_new, stack_name)
            if not update or not is_updateable:
                all_satisfied = template_deployer.all_resource_dependencies_satisfied(
                    logical_id, resource_map_new, stack_name)
                if not all_satisfied:
                    LOG.info('Resource %s cannot be deployed, found unsatisfied dependencies. %s' % (
                        logical_id, resource_json))
                    details = [logical_id, resource_json, resources_map, region_name]
                    resources_map._unresolved_resources = getattr(resources_map, '_unresolved_resources', {})
                    resources_map._unresolved_resources[logical_id] = details
                else:
                    LOG.debug('Resource %s need not be deployed (is_updateable=%s): %s %s' % (
                        logical_id, is_updateable, resource_json, bool(resource)))
                # Return if this resource already exists and can/need not be updated yet
                # NOTE: We should always return the resource here, to avoid duplicate
                #       creation of resources in moto!
                return resource

        # Apply some fixes/patches to the resource names, then deploy resource in LocalStack
        update_resource_name(resource, resource_json)
        LOG.debug('Deploying CloudFormation resource (update=%s, exists=%s, updateable=%s): %s' %
                  (update, not should_be_created, is_updateable, resource_json))

        try:
            CURRENTLY_UPDATING_RESOURCES[resource_hash_key] = True
            deploy_func = template_deployer.update_resource if update else template_deployer.deploy_resource
            result = deploy_func(logical_id, resource_map_new, stack_name=stack_name)
        finally:
            CURRENTLY_UPDATING_RESOURCES[resource_hash_key] = False

        if not should_be_created:
            # skip the parts below for update requests
            return resource

        def find_id(resource):
            """ Find ID of the given resource. """
            if not resource:
                return
            for id_attr in ('Id', 'id', 'ResourceId', 'RestApiId', 'DeploymentId', 'RoleId'):
                if id_attr in resource:
                    return resource[id_attr]

        # update resource IDs to avoid mismatch between CF moto and LocalStack backend resources
        if hasattr(resource, 'id') or (isinstance(resource, dict) and resource.get('id')):
            existing_id = resource.id if hasattr(resource, 'id') else resource['id']
            new_res_id = find_id(result)
            LOG.debug('Updating resource id: %s - %s, %s - %s' % (existing_id, new_res_id, resource, resource_json))
            if new_res_id:
                LOG.info('Updating resource ID from %s to %s (%s)' % (existing_id, new_res_id, region_name))
                update_resource_id(resource, new_res_id, props, region_name)
            else:
                LOG.warning('Unable to extract id for resource %s: %s' % (logical_id, result))

        # update physical_resource_id field
        update_physical_resource_id(resource)

        return resource

    def update_resource_name(resource, resource_json):
        """ Some resources require minor fixes in their CF resource definition
            before we can pass them on to deployment. """
        props = resource_json['Properties'] = resource_json.get('Properties') or {}
        if isinstance(resource, sfn_models.StateMachine) and not props.get('StateMachineName'):
            props['StateMachineName'] = resource.name

    def update_resource_id(resource, new_id, props, region_name):
        """ Update and fix the ID(s) of the given resource. """

        # NOTE: this is a bit of a hack, which is required because
        # of the order of events when CloudFormation resources are created.
        # When we process a request to create a CF resource that's part of a
        # stack, say, an API Gateway Resource, then we (1) create the object
        # in memory in moto, which generates a random ID for the resource, and
        # (2) create the actual resource in the backend service using
        # template_deployer.deploy_resource(..) (see above).
        # The resource created in (2) now has a different ID than the resource
        # created in (1), which leads to downstream problems. Hence, we need
        # the logic below to reconcile the ids, i.e., apply IDs from (2) to (1).

        backend = apigw_models.apigateway_backends[region_name]
        if isinstance(resource, apigw_models.RestAPI):
            backend.apis.pop(resource.id, None)
            backend.apis[new_id] = resource
            # We also need to fetch the resources to replace the root resource
            # that moto automatically adds to newly created RestAPI objects
            client = aws_stack.connect_to_service('apigateway')
            resources = client.get_resources(restApiId=new_id, limit=500)['items']
            # make sure no resources have been added in addition to the root /
            assert len(resource.resources) == 1
            resource.resources = {}
            for res in resources:
                res_path_part = res.get('pathPart') or res.get('path')
                child = resource.add_child(res_path_part, res.get('parentId'))
                resource.resources.pop(child.id)
                child.id = res['id']
                child.api_id = new_id
                resource.resources[child.id] = child
            resource.id = new_id
        elif isinstance(resource, apigw_models.Resource):
            api_id = props['RestApiId']
            backend.apis[api_id].resources.pop(resource.id, None)
            backend.apis[api_id].resources[new_id] = resource
            resource.id = new_id
        elif isinstance(resource, apigw_models.Deployment):
            api_id = props['RestApiId']
            backend.apis[api_id].deployments.pop(resource['id'], None)
            backend.apis[api_id].deployments[new_id] = resource
            resource['id'] = new_id
        else:
            LOG.warning('Unexpected resource type when updating ID: %s' % type(resource))

    parse_and_create_resource_orig = parsing.parse_and_create_resource
    parsing.parse_and_create_resource = parse_and_create_resource
    parse_and_update_resource_orig = parsing.parse_and_update_resource
    parsing.parse_and_update_resource = parse_and_update_resource

    # Patch CloudFormation parse_output(..) method to fix a bug in moto

    def parse_output(output_logical_id, output_json, resources_map):
        try:
            result = parse_output_orig(output_logical_id, output_json, resources_map)
        except KeyError:
            result = Output()
            result.key = output_logical_id
            result.value = None
            result.description = output_json.get('Description')
        # Make sure output includes export name
        if not hasattr(result, 'export_name'):
            result.export_name = output_json.get('Export', {}).get('Name')
        return result

    parse_output_orig = parsing.parse_output
    parsing.parse_output = parse_output

    # Make sure the export name is returned for stack outputs

    if '<ExportName>' not in responses.DESCRIBE_STACKS_TEMPLATE:
        find = '</OutputValue>'
        replace = """</OutputValue>
        {% if output.export_name %}
        <ExportName>{{ output.export_name }}</ExportName>
        {% endif %}
        """
        responses.DESCRIBE_STACKS_TEMPLATE = responses.DESCRIBE_STACKS_TEMPLATE.replace(find, replace)

    # Patch DynamoDB get_cfn_attribute(..) method in moto

    def DynamoDB_Table_get_cfn_attribute(self, attribute_name):
        try:
            return DynamoDB_Table_get_cfn_attribute_orig(self, attribute_name)
        except Exception:
            if attribute_name == 'Arn':
                return aws_stack.dynamodb_table_arn(table_name=self.name)
            raise

    DynamoDB_Table_get_cfn_attribute_orig = dynamodb_models.Table.get_cfn_attribute
    dynamodb_models.Table.get_cfn_attribute = DynamoDB_Table_get_cfn_attribute

    # Patch DynamoDB get_cfn_attribute(..) method in moto

    def DynamoDB2_Table_get_cfn_attribute(self, attribute_name):
        if attribute_name == 'Arn':
            return aws_stack.dynamodb_table_arn(table_name=self.name)
        elif attribute_name == 'StreamArn':
            if (self.stream_specification or {}).get('StreamEnabled'):
                return aws_stack.dynamodb_stream_arn(self.name, 'latest')
            return None
        raise UnformattedGetAttTemplateException()

    dynamodb2_models.Table.get_cfn_attribute = DynamoDB2_Table_get_cfn_attribute

    # Patch SQS get_cfn_attribute(..) method in moto

    def SQS_Queue_get_cfn_attribute(self, attribute_name):
        if attribute_name in ['Arn', 'QueueArn']:
            return aws_stack.sqs_queue_arn(queue_name=self.name)
        return SQS_Queue_get_cfn_attribute_orig(self, attribute_name)

    SQS_Queue_get_cfn_attribute_orig = sqs_models.Queue.get_cfn_attribute
    sqs_models.Queue.get_cfn_attribute = SQS_Queue_get_cfn_attribute

    # Patch S3 Bucket get_cfn_attribute(..) method in moto

    def S3_Bucket_get_cfn_attribute(self, attribute_name):
        if attribute_name in ['Arn']:
            return aws_stack.s3_bucket_arn(self.name)
        return S3_Bucket_get_cfn_attribute_orig(self, attribute_name)

    S3_Bucket_get_cfn_attribute_orig = s3_models.FakeBucket.get_cfn_attribute
    s3_models.FakeBucket.get_cfn_attribute = S3_Bucket_get_cfn_attribute

    # Patch SQS physical_resource_id(..) method in moto

    @property
    def SQS_Queue_physical_resource_id(self):
        result = SQS_Queue_physical_resource_id_orig.fget(self)
        if '://' not in result:
            # convert ID to queue URL
            return aws_stack.get_sqs_queue_url(result)
        return result

    SQS_Queue_physical_resource_id_orig = sqs_models.Queue.physical_resource_id
    sqs_models.Queue.physical_resource_id = SQS_Queue_physical_resource_id

    # Patch LogGroup get_cfn_attribute(..) method in moto

    def LogGroup_get_cfn_attribute(self, attribute_name):
        try:
            return LogGroup_get_cfn_attribute_orig(self, attribute_name)
        except Exception:
            if attribute_name == 'Arn':
                return aws_stack.log_group_arn(self.name)
            raise

    LogGroup_get_cfn_attribute_orig = getattr(cw_models.LogGroup, 'get_cfn_attribute', None)
    cw_models.LogGroup.get_cfn_attribute = LogGroup_get_cfn_attribute

    # Patch Lambda get_cfn_attribute(..) method in moto

    def Lambda_Function_get_cfn_attribute(self, attribute_name):
        try:
            if attribute_name == 'Arn':
                return self.function_arn
            return Lambda_Function_get_cfn_attribute_orig(self, attribute_name)
        except Exception:
            if attribute_name in ('Name', 'FunctionName'):
                return self.function_name
            raise

    Lambda_Function_get_cfn_attribute_orig = lambda_models.LambdaFunction.get_cfn_attribute
    lambda_models.LambdaFunction.get_cfn_attribute = Lambda_Function_get_cfn_attribute

    # Patch DynamoDB get_cfn_attribute(..) method in moto

    def DynamoDB_Table_get_cfn_attribute(self, attribute_name):
        try:
            if attribute_name == 'StreamArn':
                streams = aws_stack.connect_to_service('dynamodbstreams').list_streams(TableName=self.name)['Streams']
                return streams[0]['StreamArn'] if streams else None
            return DynamoDB_Table_get_cfn_attribute_orig(self, attribute_name)
        except Exception as e:
            LOG.warning('Unable to get attribute "%s" from resource %s: %s' % (attribute_name, type(self), e))
            raise

    DynamoDB_Table_get_cfn_attribute_orig = dynamodb_models.Table.get_cfn_attribute
    dynamodb_models.Table.get_cfn_attribute = DynamoDB_Table_get_cfn_attribute

    # Patch IAM get_cfn_attribute(..) method in moto

    def IAM_Role_get_cfn_attribute(self, attribute_name):
        try:
            return IAM_Role_get_cfn_attribute_orig(self, attribute_name)
        except Exception:
            if attribute_name == 'Arn':
                return aws_stack.role_arn(self.name)
            raise

    IAM_Role_get_cfn_attribute_orig = iam_models.Role.get_cfn_attribute
    iam_models.Role.get_cfn_attribute = IAM_Role_get_cfn_attribute

    # Patch SNS Topic get_cfn_attribute(..) method in moto

    def SNS_Topic_get_cfn_attribute(self, attribute_name):
        result = SNS_Topic_get_cfn_attribute_orig(self, attribute_name)
        if attribute_name.lower() in ['arn', 'topicarn']:
            result = aws_stack.fix_account_id_in_arns(result)
        return result

    SNS_Topic_get_cfn_attribute_orig = sns_models.Topic.get_cfn_attribute
    sns_models.Topic.get_cfn_attribute = SNS_Topic_get_cfn_attribute

    # Patch LambdaFunction create_from_cloudformation_json(..) method in moto

    @classmethod
    def Lambda_create_from_cloudformation_json(cls, resource_name, cloudformation_json, region_name):
        resource_name = cloudformation_json.get('Properties', {}).get('FunctionName') or resource_name
        return Lambda_create_from_cloudformation_json_orig(resource_name, cloudformation_json, region_name)

    Lambda_create_from_cloudformation_json_orig = lambda_models.LambdaFunction.create_from_cloudformation_json
    lambda_models.LambdaFunction.create_from_cloudformation_json = Lambda_create_from_cloudformation_json

    # Patch EventSourceMapping create_from_cloudformation_json(..) method in moto

    @classmethod
    def Mapping_create_from_cloudformation_json(cls, resource_name, cloudformation_json, region_name):
        props = cloudformation_json.get('Properties', {})
        func_name = props.get('FunctionName') or ''
        if ':lambda:' in func_name:
            props['FunctionName'] = aws_stack.lambda_function_name(func_name)
        return Mapping_create_from_cloudformation_json_orig(resource_name, cloudformation_json, region_name)

    Mapping_create_from_cloudformation_json_orig = lambda_models.EventSourceMapping.create_from_cloudformation_json
    lambda_models.EventSourceMapping.create_from_cloudformation_json = Mapping_create_from_cloudformation_json

    # Patch LambdaFunction update_from_cloudformation_json(..) method in moto

    @classmethod
    def Lambda_update_from_cloudformation_json(cls,
            original_resource, new_resource_name, cloudformation_json, region_name):
        resource_name = cloudformation_json.get('Properties', {}).get('FunctionName') or new_resource_name
        return Lambda_create_from_cloudformation_json_orig(resource_name, cloudformation_json, region_name)

    if not hasattr(lambda_models.LambdaFunction, 'update_from_cloudformation_json'):
        lambda_models.LambdaFunction.update_from_cloudformation_json = Lambda_update_from_cloudformation_json

    # patch ApiGateway Deployment

    def depl_delete_from_cloudformation_json(
            resource_name, resource_json, region_name):
        properties = resource_json['Properties']
        LOG.info('TODO: apigateway.Deployment.delete_from_cloudformation_json %s' % properties)

    if not hasattr(apigw_models.Deployment, 'delete_from_cloudformation_json'):
        apigw_models.Deployment.delete_from_cloudformation_json = depl_delete_from_cloudformation_json

    # patch Lambda Version

    def vers_delete_from_cloudformation_json(
            resource_name, resource_json, region_name):
        properties = resource_json['Properties']
        LOG.info('TODO: apigateway.Deployment.delete_from_cloudformation_json %s' % properties)

    if not hasattr(lambda_models.LambdaVersion, 'delete_from_cloudformation_json'):
        lambda_models.LambdaVersion.delete_from_cloudformation_json = vers_delete_from_cloudformation_json

    # add CloudFormation types

    @classmethod
    def RestAPI_create_from_cloudformation_json(cls, resource_name, cloudformation_json, region_name):
        props = cloudformation_json['Properties']
        name = props['Name']
        region_name = props.get('Region') or aws_stack.get_region()
        description = props.get('Description') or ''
        id = props.get('Id') or short_uid()
        return apigw_models.RestAPI(id, region_name, name, description)

    def RestAPI_get_cfn_attribute(self, attribute_name):
        if attribute_name == 'Id':
            return self.id
        if attribute_name == 'Region':
            return self.region_name
        if attribute_name == 'Name':
            return self.name
        if attribute_name == 'Description':
            return self.description
        if attribute_name == 'RootResourceId':
            for id, resource in self.resources.items():
                if resource.parent_id is None:
                    return resource.id
            return None
        raise UnformattedGetAttTemplateException()

    @classmethod
    def Deployment_create_from_cloudformation_json(cls, resource_name, cloudformation_json, region_name):
        props = cloudformation_json['Properties']
        name = props['StageName']
        deployment_id = props.get('Id') or short_uid()
        description = props.get('Description') or ''
        return apigw_models.Deployment(deployment_id, name, description)

    @classmethod
    def Resource_create_from_cloudformation_json(cls, resource_name, cloudformation_json, region_name):
        props = cloudformation_json['Properties']
        region_name = props.get('Region') or aws_stack.get_region()
        path_part = props.get('PathPart')
        api_id = props.get('RestApiId')
        parent_id = props.get('ParentId')
        id = props.get('Id') or short_uid()
        return apigw_models.Resource(id, region_name, api_id, path_part, parent_id)

    @classmethod
    def Method_create_from_cloudformation_json(cls, resource_name, cloudformation_json, region_name):
        props = cloudformation_json['Properties']
        method_type = props.get('HttpMethod')
        authorization_type = props.get('AuthorizationType')
        return apigw_models.Method(method_type, authorization_type)

    apigw_models.RestAPI.create_from_cloudformation_json = RestAPI_create_from_cloudformation_json
    apigw_models.RestAPI.get_cfn_attribute = RestAPI_get_cfn_attribute
    apigw_models.Deployment.create_from_cloudformation_json = Deployment_create_from_cloudformation_json
    apigw_models.Resource.create_from_cloudformation_json = Resource_create_from_cloudformation_json
    apigw_models.Method.create_from_cloudformation_json = Method_create_from_cloudformation_json
    # TODO: add support for AWS::ApiGateway::Model, AWS::ApiGateway::RequestValidator, ...

    # fix AttributeError in moto's CloudFormation describe_stack_resource

    def describe_stack_resource(self):
        stack_name = self._get_param('StackName')
        stack = self.cloudformation_backend.get_stack(stack_name)
        logical_resource_id = self._get_param('LogicalResourceId')
        if not stack:
            msg = ('Unable to find CloudFormation stack "%s" in region %s' %
                   (stack_name, aws_stack.get_region()))
            if aws_stack.get_region() != self.region:
                msg = '%s/%s' % (msg, self.region)
            LOG.warning(msg)
            response = aws_responses.flask_error_response(msg, code=404, error_type='ResourceNotFoundException')
            return 404, response.headers, response.data

        for stack_resource in stack.stack_resources:
            # Note: Line below has been patched
            # if stack_resource.logical_resource_id == logical_resource_id:
            if stack_resource and stack_resource.logical_resource_id == logical_resource_id:
                resource = stack_resource
                break
        else:
            raise ValidationError(logical_resource_id)

        template = self.response_template(
            responses.DESCRIBE_STACK_RESOURCE_RESPONSE_TEMPLATE)
        return template.render(stack=stack, resource=resource)

    responses.CloudFormationResponse.describe_stack_resource = describe_stack_resource

    # fix moto's describe_stack_events jinja2.exceptions.UndefinedError

    def cf_describe_stack_events(self):
        stack_name = self._get_param('StackName')
        backend = self.cloudformation_backend
        stack = backend.get_stack(stack_name)
        if not stack:
            # Also return stack events for deleted stacks, specified by stack name
            stack = ([stk for id, stk in backend.deleted_stacks.items() if stk.name == stack_name] or [0])[0]
        if not stack:
            raise ValidationError(stack_name,
                message='Unable to find stack "%s" in region %s' % (stack_name, aws_stack.get_region()))
        template = self.response_template(responses.DESCRIBE_STACK_EVENTS_RESPONSE)
        return template.render(stack=stack)

    responses.CloudFormationResponse.describe_stack_events = cf_describe_stack_events

    # fix Lambda regions in moto - see https://github.com/localstack/localstack/issues/1961

    for region in boto3.session.Session().get_available_regions('lambda'):
        if region not in lambda_models.lambda_backends:
            lambda_models.lambda_backends[region] = lambda_models.LambdaBackend(region)

    # patch FakeStack.initialize_resources

    def initialize_resources(self):
        def set_status(status):
            self._add_stack_event(status)
            self.status = status

        self.resource_map.create()
        self.output_map.create()

        def run_loop(*args):
            # NOTE: We're adding this additional loop, as it seems that in some cases moto
            #   does not consider resource dependencies (e.g., if a "DependsOn" resource property
            #   is defined). This loop allows us to incrementally resolve such dependencies.
            resource_map = self.resource_map
            unresolved = {}
            for i in range(MAX_DEPENDENCY_DEPTH):
                unresolved = getattr(resource_map, '_unresolved_resources', {})
                if not unresolved:
                    set_status('CREATE_COMPLETE')
                    return resource_map
                resource_map._unresolved_resources = {}
                for resource_id, resource_details in unresolved.items():
                    # Re-trigger the resource creation
                    parse_and_create_resource(*resource_details, force_create=True)
                if unresolved.keys() == resource_map._unresolved_resources.keys():
                    # looks like no more resources can be resolved -> bail
                    LOG.warning('Unresolvable dependencies, there may be undeployed stack resources: %s' % unresolved)
                    break
            set_status('CREATE_FAILED')
            raise Exception('Unable to resolve all CloudFormation resources after traversing ' +
                'dependency tree (maximum depth %s reached): %s' % (MAX_DEPENDENCY_DEPTH, unresolved.keys()))

        # NOTE: We're running the loop in the background, as it might take some time to complete
        FuncThread(run_loop).start()

    FakeStack.initialize_resources = initialize_resources