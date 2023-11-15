def post_request():
    action = request.headers.get('x-amz-target')
    data = json.loads(to_str(request.data))
    response = None
    if action == '%s.ListDeliveryStreams' % ACTION_HEADER_PREFIX:
        response = {
            'DeliveryStreamNames': get_delivery_stream_names(),
            'HasMoreDeliveryStreams': False
        }
    elif action == '%s.CreateDeliveryStream' % ACTION_HEADER_PREFIX:
        stream_name = data['DeliveryStreamName']
        region_name = extract_region_from_auth_header(request.headers)
        response = create_stream(
            stream_name, delivery_stream_type=data.get('DeliveryStreamType'),
            delivery_stream_type_configuration=data.get('KinesisStreamSourceConfiguration'),
            s3_destination=data.get('S3DestinationConfiguration'),
            elasticsearch_destination=data.get('ElasticsearchDestinationConfiguration'),
            tags=data.get('Tags'), region_name=region_name)
    elif action == '%s.DeleteDeliveryStream' % ACTION_HEADER_PREFIX:
        stream_name = data['DeliveryStreamName']
        response = delete_stream(stream_name)
    elif action == '%s.DescribeDeliveryStream' % ACTION_HEADER_PREFIX:
        stream_name = data['DeliveryStreamName']
        response = get_stream(stream_name)
        if not response:
            return error_not_found(stream_name)
        response = {
            'DeliveryStreamDescription': response
        }
    elif action == '%s.PutRecord' % ACTION_HEADER_PREFIX:
        stream_name = data['DeliveryStreamName']
        record = data['Record']
        put_record(stream_name, record)
        response = {
            'RecordId': str(uuid.uuid4())
        }
    elif action == '%s.PutRecordBatch' % ACTION_HEADER_PREFIX:
        stream_name = data['DeliveryStreamName']
        records = data['Records']
        put_records(stream_name, records)
        request_responses = []
        for i in records:
            request_responses.append({'RecordId': str(uuid.uuid4())})
        response = {
            'FailedPutCount': 0,
            'RequestResponses': request_responses
        }
    elif action == '%s.UpdateDestination' % ACTION_HEADER_PREFIX:
        stream_name = data['DeliveryStreamName']
        version_id = data['CurrentDeliveryStreamVersionId']
        destination_id = data['DestinationId']
        s3_update = data['S3DestinationUpdate'] if 'S3DestinationUpdate' in data else None
        update_destination(stream_name=stream_name, destination_id=destination_id,
                           s3_update=s3_update, version_id=version_id)
        es_update = data['ESDestinationUpdate'] if 'ESDestinationUpdate' in data else None
        update_destination(stream_name=stream_name, destination_id=destination_id,
                           es_update=es_update, version_id=version_id)
        response = {}
    elif action == '%s.ListTagsForDeliveryStream' % ACTION_HEADER_PREFIX:
        response = get_delivery_stream_tags(data['DeliveryStreamName'], data.get('ExclusiveStartTagKey'),
                                            data.get('Limit', 50))
    else:
        response = error_response('Unknown action "%s"' % action, code=400, error_type='InvalidAction')

    if isinstance(response, dict):
        response = jsonify(response)
    return response