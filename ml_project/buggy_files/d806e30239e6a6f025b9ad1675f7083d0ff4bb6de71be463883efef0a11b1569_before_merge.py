def send_event_to_target(arn, event):
    if ':lambda:' in arn:
        from localstack.services.awslambda import lambda_api
        lambda_api.run_lambda(event=event, context={}, func_arn=arn)

    elif ':sns:' in arn:
        sns_client = connect_to_service('sns')
        sns_client.publish(TopicArn=arn, Message=json.dumps(event))

    elif ':sqs:' in arn:
        sqs_client = connect_to_service('sqs')
        queue_url = get_sqs_queue_url(arn)
        sqs_client.send_message(QueueUrl=queue_url, MessageBody=json.dumps(event))

    elif ':states' in arn:
        stepfunctions_client = connect_to_service('stepfunctions')
        stepfunctions_client.start_execution(stateMachineArn=arn, input=json.dumps(event))

    else:
        LOG.info('Unsupported Events rule target ARN "%s"' % arn)