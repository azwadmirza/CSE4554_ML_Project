    def forward_request(self, method, path, data, headers):

        if method == 'POST' and path == '/':
            req_data = urlparse.parse_qs(to_str(data))
            req_action = req_data['Action'][0]
            topic_arn = req_data.get('TargetArn') or req_data.get('TopicArn')

            if topic_arn:
                topic_arn = topic_arn[0]
                do_create_topic(topic_arn)

            if req_action == 'SetSubscriptionAttributes':
                sub = get_subscription_by_arn(req_data['SubscriptionArn'][0])
                if not sub:
                    return make_error(message='Unable to find subscription for given ARN', code=400)
                attr_name = req_data['AttributeName'][0]
                attr_value = req_data['AttributeValue'][0]
                sub[attr_name] = attr_value
                return make_response(req_action)
            elif req_action == 'GetSubscriptionAttributes':
                sub = get_subscription_by_arn(req_data['SubscriptionArn'][0])
                if not sub:
                    return make_error(message='Unable to find subscription for given ARN', code=400)
                content = '<Attributes>'
                for key, value in sub.items():
                    content += '<entry><key>%s</key><value>%s</value></entry>\n' % (key, value)
                content += '</Attributes>'
                return make_response(req_action, content=content)
            elif req_action == 'Subscribe':
                if 'Endpoint' not in req_data:
                    return make_error(message='Endpoint not specified in subscription', code=400)
            elif req_action == 'Unsubscribe':
                if 'SubscriptionArn' not in req_data:
                    return make_error(message='SubscriptionArn not specified in unsubscribe request', code=400)
                do_unsubscribe(req_data.get('SubscriptionArn')[0])

            elif req_action == 'Publish':
                message = req_data['Message'][0]
                sqs_client = aws_stack.connect_to_service('sqs')
                for subscriber in SNS_SUBSCRIPTIONS[topic_arn]:
                    if subscriber['Protocol'] == 'sqs':
                        queue_name = subscriber['Endpoint'].split(':')[5]
                        queue_url = subscriber.get('sqs_queue_url')
                        if not queue_url:
                            queue_url = aws_stack.get_sqs_queue_url(queue_name)
                            subscriber['sqs_queue_url'] = queue_url
                        sqs_client.send_message(QueueUrl=queue_url,
                            MessageBody=create_sns_message_body(subscriber, req_data))
                    elif subscriber['Protocol'] == 'lambda':
                        lambda_api.process_sns_notification(
                            subscriber['Endpoint'],
                            topic_arn, message, subject=req_data.get('Subject')
                        )
                    elif subscriber['Protocol'] in ['http', 'https']:
                        requests.post(
                            subscriber['Endpoint'],
                            headers={
                                'Content-Type': 'text/plain',
                                'x-amz-sns-message-type': 'Notification'
                            },
                            data=create_sns_message_body(subscriber, req_data))
                    else:
                        LOGGER.warning('Unexpected protocol "%s" for SNS subscription' % subscriber['Protocol'])
                # return response here because we do not want the request to be forwarded to SNS
                return make_response(req_action)

        return True