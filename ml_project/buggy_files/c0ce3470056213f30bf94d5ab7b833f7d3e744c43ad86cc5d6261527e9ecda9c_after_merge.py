def send_notifications(method, bucket_name, object_path, version_id):
    for bucket, notifs in S3_NOTIFICATIONS.items():
        if bucket == bucket_name:
            action = {'PUT': 'ObjectCreated', 'POST': 'ObjectCreated', 'DELETE': 'ObjectRemoved'}[method]
            # TODO: support more detailed methods, e.g., DeleteMarkerCreated
            # http://docs.aws.amazon.com/AmazonS3/latest/dev/NotificationHowTo.html
            if action == 'ObjectCreated' and method == 'POST':
                api_method = 'CompleteMultipartUpload'
            else:
                api_method = {'PUT': 'Put', 'POST': 'Post', 'DELETE': 'Delete'}[method]

            event_name = '%s:%s' % (action, api_method)
            for notif in notifs:
                send_notification_for_subscriber(notif, bucket_name, object_path,
                    version_id, api_method, action, event_name)