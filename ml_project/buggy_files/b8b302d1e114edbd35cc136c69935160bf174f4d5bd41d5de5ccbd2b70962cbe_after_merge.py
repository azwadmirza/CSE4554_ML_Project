    def forward_request(self, method, path, data, headers):
        result = handle_special_request(method, path, data, headers)
        if result is not None:
            return result

        if not data:
            data = '{}'
        data = json.loads(to_str(data))
        ddb_client = aws_stack.connect_to_service('dynamodb')
        action = headers.get('X-Amz-Target')

        if self.should_throttle(action):
            return error_response_throughput()

        ProxyListenerDynamoDB.thread_local.existing_item = None

        if action == '%s.CreateTable' % ACTION_PREFIX:
            # Check if table exists, to avoid error log output from DynamoDBLocal
            if self.table_exists(ddb_client, data['TableName']):
                return error_response(message='Table already created',
                                      error_type='ResourceInUseException', code=400)

        if action == '%s.CreateGlobalTable' % ACTION_PREFIX:
            return create_global_table(data)

        elif action == '%s.DescribeGlobalTable' % ACTION_PREFIX:
            return describe_global_table(data)

        elif action == '%s.ListGlobalTables' % ACTION_PREFIX:
            return list_global_tables(data)

        elif action == '%s.UpdateGlobalTable' % ACTION_PREFIX:
            return update_global_table(data)

        elif action in ('%s.PutItem' % ACTION_PREFIX, '%s.UpdateItem' % ACTION_PREFIX, '%s.DeleteItem' % ACTION_PREFIX):
            # find an existing item and store it in a thread-local, so we can access it in return_response,
            # in order to determine whether an item already existed (MODIFY) or not (INSERT)
            try:
                if has_event_sources_or_streams_enabled(data['TableName']):
                    ProxyListenerDynamoDB.thread_local.existing_item = find_existing_item(data)
            except Exception as e:
                if 'ResourceNotFoundException' in str(e):
                    return get_table_not_found_error()
                raise

            # Fix incorrect values if ReturnValues==ALL_OLD and ReturnConsumedCapacity is
            # empty, see https://github.com/localstack/localstack/issues/2049
            if ((data.get('ReturnValues') == 'ALL_OLD') or (not data.get('ReturnValues'))) \
                    and not data.get('ReturnConsumedCapacity'):
                data['ReturnConsumedCapacity'] = 'TOTAL'
                return Request(data=json.dumps(data), method=method, headers=headers)

        elif action == '%s.DescribeTable' % ACTION_PREFIX:
            # Check if table exists, to avoid error log output from DynamoDBLocal
            if not self.table_exists(ddb_client, data['TableName']):
                return get_table_not_found_error()

        elif action == '%s.DeleteTable' % ACTION_PREFIX:
            # Check if table exists, to avoid error log output from DynamoDBLocal
            if not self.table_exists(ddb_client, data['TableName']):
                return get_table_not_found_error()

        elif action == '%s.BatchWriteItem' % ACTION_PREFIX:
            existing_items = []
            for table_name in sorted(data['RequestItems'].keys()):
                for request in data['RequestItems'][table_name]:
                    for key in ['PutRequest', 'DeleteRequest']:
                        inner_request = request.get(key)
                        if inner_request:
                            existing_items.append(find_existing_item(inner_request, table_name))
            ProxyListenerDynamoDB.thread_local.existing_items = existing_items

        elif action == '%s.Query' % ACTION_PREFIX:
            if data.get('IndexName'):
                if not is_index_query_valid(to_str(data['TableName']), data.get('Select')):
                    return error_response(message='One or more parameter values were invalid: Select type '
                                                  'ALL_ATTRIBUTES is not supported for global secondary index id-index '
                                                  'because its projection type is not ALL',
                                          error_type='ValidationException', code=400)

        elif action == '%s.TransactWriteItems' % ACTION_PREFIX:
            existing_items = []
            for item in data['TransactItems']:
                for key in ['Put', 'Update', 'Delete']:
                    inner_item = item.get(key)
                    if inner_item:
                        existing_items.append(find_existing_item(inner_item))
            ProxyListenerDynamoDB.thread_local.existing_items = existing_items

        elif action == '%s.UpdateTimeToLive' % ACTION_PREFIX:
            # TODO: TTL status is maintained/mocked but no real expiry is happening for items
            response = Response()
            response.status_code = 200
            self._table_ttl_map[data['TableName']] = {
                'AttributeName': data['TimeToLiveSpecification']['AttributeName'],
                'Status': data['TimeToLiveSpecification']['Enabled']
            }
            response._content = json.dumps({'TimeToLiveSpecification': data['TimeToLiveSpecification']})
            fix_headers_for_updated_response(response)
            return response

        elif action == '%s.DescribeTimeToLive' % ACTION_PREFIX:
            response = Response()
            response.status_code = 200
            if data['TableName'] in self._table_ttl_map:
                if self._table_ttl_map[data['TableName']]['Status']:
                    ttl_status = 'ENABLED'
                else:
                    ttl_status = 'DISABLED'
                response._content = json.dumps({
                    'TimeToLiveDescription': {
                        'AttributeName': self._table_ttl_map[data['TableName']]['AttributeName'],
                        'TimeToLiveStatus': ttl_status
                    }
                })
            else:  # TTL for dynamodb table not set
                response._content = json.dumps({'TimeToLiveDescription': {'TimeToLiveStatus': 'DISABLED'}})

            fix_headers_for_updated_response(response)
            return response

        elif action == '%s.TagResource' % ACTION_PREFIX or action == '%s.UntagResource' % ACTION_PREFIX:
            response = Response()
            response.status_code = 200
            response._content = ''  # returns an empty body on success.
            fix_headers_for_updated_response(response)
            return response

        elif action == '%s.ListTagsOfResource' % ACTION_PREFIX:
            response = Response()
            response.status_code = 200
            response._content = json.dumps({
                'Tags': [
                    {'Key': k, 'Value': v}
                    for k, v in TABLE_TAGS.get(data['ResourceArn'], {}).items()
                ]
            })
            fix_headers_for_updated_response(response)
            return response

        return True