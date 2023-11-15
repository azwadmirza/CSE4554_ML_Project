def send_notifications(method, bucket_name, object_path, version_id):
    for bucket, b_cfg in iteritems(S3_NOTIFICATIONS):
        if bucket == bucket_name:
            action = {'PUT': 'ObjectCreated', 'POST': 'ObjectCreated', 'DELETE': 'ObjectRemoved'}[method]
            # TODO: support more detailed methods, e.g., DeleteMarkerCreated
            # http://docs.aws.amazon.com/AmazonS3/latest/dev/NotificationHowTo.html
            if action == 'ObjectCreated' and method == 'POST':
                api_method = 'CompleteMultipartUpload'
            else:
                api_method = {'PUT': 'Put', 'POST': 'Post', 'DELETE': 'Delete'}[method]

            event_name = '%s:%s' % (action, api_method)
            if (event_type_matches(b_cfg['Event'], action, api_method) and
                    filter_rules_match(b_cfg.get('Filter'), object_path)):
                # send notification
                message = get_event_message(
                    event_name=event_name, bucket_name=bucket_name,
                    file_name=urlparse.urlparse(object_path[1:]).path,
                    version_id=version_id
                )
                message = json.dumps(message)
                if b_cfg.get('Queue'):
                    sqs_client = aws_stack.connect_to_service('sqs')
                    try:
                        queue_url = queue_url_for_arn(b_cfg['Queue'])
                        sqs_client.send_message(QueueUrl=queue_url, MessageBody=message)
                    except Exception as e:
                        LOGGER.warning('Unable to send notification for S3 bucket "%s" to SQS queue "%s": %s' %
                            (bucket_name, b_cfg['Queue'], e))
                if b_cfg.get('Topic'):
                    sns_client = aws_stack.connect_to_service('sns')
                    try:
                        sns_client.publish(TopicArn=b_cfg['Topic'], Message=message, Subject='Amazon S3 Notification')
                    except Exception:
                        LOGGER.warning('Unable to send notification for S3 bucket "%s" to SNS topic "%s".' %
                            (bucket_name, b_cfg['Topic']))
                # CloudFunction and LambdaFunction are semantically identical
                lambda_function_config = b_cfg.get('CloudFunction') or b_cfg.get('LambdaFunction')
                if lambda_function_config:
                    # make sure we don't run into a socket timeout
                    connection_config = botocore.config.Config(read_timeout=300)
                    lambda_client = aws_stack.connect_to_service('lambda', config=connection_config)
                    try:
                        lambda_client.invoke(FunctionName=lambda_function_config,
                                             InvocationType='Event', Payload=message)
                    except Exception:
                        LOGGER.warning('Unable to send notification for S3 bucket "%s" to Lambda function "%s".' %
                            (bucket_name, lambda_function_config))
                if not filter(lambda x: b_cfg.get(x), NOTIFICATION_DESTINATION_TYPES):
                    LOGGER.warning('Neither of %s defined for S3 notification.' %
                        '/'.join(NOTIFICATION_DESTINATION_TYPES))