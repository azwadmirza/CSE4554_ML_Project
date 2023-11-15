    def return_response(self, method, path, data, headers, response):
        action = headers.get('X-Amz-Target')
        data = json.loads(to_str(data))

        records = []
        if action in (ACTION_CREATE_STREAM, ACTION_DELETE_STREAM):
            event_type = (event_publisher.EVENT_KINESIS_CREATE_STREAM if action == ACTION_CREATE_STREAM
                          else event_publisher.EVENT_KINESIS_DELETE_STREAM)
            payload = {'n': event_publisher.get_hash(data.get('StreamName'))}
            if action == ACTION_CREATE_STREAM:
                payload['s'] = data.get('ShardCount')
            event_publisher.fire_event(event_type, payload=payload)
        elif action == ACTION_PUT_RECORD:
            response_body = json.loads(to_str(response.content))
            event_record = {
                'data': data['Data'],
                'partitionKey': data['PartitionKey'],
                'sequenceNumber': response_body.get('SequenceNumber')
            }
            event_records = [event_record]
            stream_name = data['StreamName']
            lambda_api.process_kinesis_records(event_records, stream_name)
        elif action == ACTION_PUT_RECORDS:
            event_records = []
            response_body = json.loads(to_str(response.content))
            response_records = response_body['Records']
            records = data['Records']
            for index in range(0, len(records)):
                record = records[index]
                event_record = {
                    'data': record['Data'],
                    'partitionKey': record['PartitionKey'],
                    'sequenceNumber': response_records[index].get('SequenceNumber')
                }
                event_records.append(event_record)
            stream_name = data['StreamName']
            lambda_api.process_kinesis_records(event_records, stream_name)
        elif action == ACTION_UPDATE_SHARD_COUNT:
            # Currently kinesalite, which backs the Kinesis implementation for localstack, does
            # not support UpdateShardCount:
            # https://github.com/mhart/kinesalite/issues/61
            #
            # [Terraform](https://www.terraform.io) makes the call to UpdateShardCount when it
            # applies Kinesis resources. A Terraform run fails when this is not present.
            #
            # The code that follows just returns a successful response, bypassing the 400
            # response that kinesalite returns.
            #
            response = Response()
            response.status_code = 200
            content = {
                'CurrentShardCount': 1,
                'StreamName': data['StreamName'],
                'TargetShardCount': data['TargetShardCount']
            }
            response.encoding = 'UTF-8'
            response._content = json.dumps(content)
            return response