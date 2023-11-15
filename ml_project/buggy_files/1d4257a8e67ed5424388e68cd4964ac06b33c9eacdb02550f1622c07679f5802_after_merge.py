def post_request():
    action = request.headers.get('x-amz-target')
    data = json.loads(to_str(request.data))
    result = {}
    kinesis = aws_stack.connect_to_service('kinesis')
    if action == '%s.ListStreams' % ACTION_HEADER_PREFIX:
        result = {
            'Streams': list(DDB_STREAMS.values()),
            'LastEvaluatedStreamArn': 'TODO'
        }
    elif action == '%s.DescribeStream' % ACTION_HEADER_PREFIX:
        for stream in DDB_STREAMS.values():
            if stream['StreamArn'] == data['StreamArn']:
                result = {
                    'StreamDescription': stream
                }
                # get stream details
                dynamodb = aws_stack.connect_to_service('dynamodb')
                table_name = table_name_from_stream_arn(stream['StreamArn'])
                stream_name = get_kinesis_stream_name(table_name)
                stream_details = kinesis.describe_stream(StreamName=stream_name)
                table_details = dynamodb.describe_table(TableName=table_name)
                stream['KeySchema'] = table_details['Table']['KeySchema']
                stream['Shards'] = stream_details['StreamDescription']['Shards']
                break
        if not result:
            return error_response('Requested resource not found', error_type='ResourceNotFoundException')
    elif action == '%s.GetShardIterator' % ACTION_HEADER_PREFIX:
        # forward request to Kinesis API
        stream_name = stream_name_from_stream_arn(data['StreamArn'])
        result = kinesis.get_shard_iterator(StreamName=stream_name,
            ShardId=data['ShardId'], ShardIteratorType=data['ShardIteratorType'])
    elif action == '%s.GetRecords' % ACTION_HEADER_PREFIX:
        kinesis_records = kinesis.get_records(**data)
        result = {'Records': []}
        for record in kinesis_records['Records']:
            result['Records'].append(json.loads(to_str(record['Data'])))
    else:
        print('WARNING: Unknown operation "%s"' % action)
    return jsonify(result)