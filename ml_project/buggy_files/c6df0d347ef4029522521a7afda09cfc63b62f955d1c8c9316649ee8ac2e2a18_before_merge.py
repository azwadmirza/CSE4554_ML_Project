def update_dynamodb(method, path, data, headers, response=None, return_forward_info=False):
    if return_forward_info:
        if random.random() < config.DYNAMODB_ERROR_PROBABILITY:
            return dynamodb_error_response(data)
        return True

    # update table definitions
    if data and 'TableName' in data and 'KeySchema' in data:
        TABLE_DEFINITIONS[data['TableName']] = data

    action = headers.get('X-Amz-Target')
    if not action:
        return

    response_data = json.loads(to_str(response.content))
    record = {
        "eventID": "1",
        "eventVersion": "1.0",
        "dynamodb": {
            "StreamViewType": "NEW_AND_OLD_IMAGES",
            "SequenceNumber": "1",
            "SizeBytes": -1
        },
        "awsRegion": DEFAULT_REGION,
        "eventSource": "aws:dynamodb"
    }
    event = {
        'Records': [record]
    }

    if action == 'DynamoDB_20120810.UpdateItem':
        req = {'TableName': data['TableName'], 'Key': data['Key']}
        new_item = aws_stack.dynamodb_get_item_raw(req)
        if 'Item' not in new_item:
            if 'message' in new_item:
                ddb_client = aws_stack.connect_to_service('dynamodb')
                table_names = ddb_client.list_tables()['TableNames']
                msg = 'Unable to get item from DynamoDB (existing tables: %s): %s' % (table_names, new_item['message'])
                LOGGER.warning(msg)
            return
        record['eventName'] = 'MODIFY'
        record['dynamodb']['Keys'] = data['Key']
        record['dynamodb']['NewImage'] = new_item['Item']
    elif action == 'DynamoDB_20120810.PutItem':
        record['eventName'] = 'INSERT'
        keys = dynamodb_extract_keys(item=data['Item'], table_name=data['TableName'])
        record['dynamodb']['Keys'] = keys
        record['dynamodb']['NewImage'] = data['Item']
    elif action == 'DynamoDB_20120810.DeleteItem':
        record['eventName'] = 'REMOVE'
        record['dynamodb']['Keys'] = data['Key']
    elif action == 'DynamoDB_20120810.CreateTable':
        if 'StreamSpecification' in data:
            stream = data['StreamSpecification']
            enabled = stream['StreamEnabled']
            if enabled:
                table_name = data['TableName']
                view_type = stream['StreamViewType']
                dynamodbstreams_api.add_dynamodb_stream(table_name=table_name,
                    view_type=view_type, enabled=enabled)
        return
    else:
        # nothing to do
        return
    record['eventSourceARN'] = aws_stack.dynamodb_table_arn(data['TableName'])
    sources = lambda_api.get_event_sources(source_arn=record['eventSourceARN'])
    if len(sources) > 0:
        pass
    for src in sources:
        func_to_call = lambda_api.lambda_arn_to_function[src['FunctionArn']]
        lambda_api.run_lambda(func_to_call, event=event, context={}, func_arn=src['FunctionArn'])