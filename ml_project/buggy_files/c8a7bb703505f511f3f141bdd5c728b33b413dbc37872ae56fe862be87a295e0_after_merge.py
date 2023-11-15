def handle_push_notification(user_profile_id, missed_message):
    # type: (int, Dict[str, Any]) -> None
    """
    missed_message is the event received by the
    zerver.worker.queue_processors.PushNotificationWorker.consume function.
    """
    try:
        user_profile = get_user_profile_by_id(user_profile_id)
        if not (receives_offline_notifications(user_profile) or receives_online_notifications(user_profile)):
            return

        umessage = UserMessage.objects.get(user_profile=user_profile,
                                           message__id=missed_message['message_id'])
        message = umessage.message
        if umessage.flags.read:
            return

        apns_payload = get_apns_payload(message)
        gcm_payload = get_gcm_payload(user_profile, message)

        if uses_notification_bouncer():
            try:
                send_notifications_to_bouncer(user_profile_id,
                                              apns_payload,
                                              gcm_payload)
            except requests.ConnectionError:
                if 'failed_tries' not in missed_message:
                    missed_message['failed_tries'] = 0

                def failure_processor(event):
                    # type: (Dict[str, Any]) -> None
                    logging.warning("Maximum retries exceeded for trigger:%s event:push_notification" % (event['user_profile_id']))
                retry_event('missedmessage_mobile_notifications', missed_message,
                            failure_processor)

            return

        android_devices = list(PushDeviceToken.objects.filter(user=user_profile,
                                                              kind=PushDeviceToken.GCM))

        apple_devices = list(PushDeviceToken.objects.filter(user=user_profile,
                                                            kind=PushDeviceToken.APNS))

        # TODO: set badge count in a better way
        if apple_devices:
            send_apple_push_notification(user_profile.id, apple_devices,
                                         badge=1, zulip=apns_payload)

        if android_devices:
            send_android_push_notification(android_devices, gcm_payload)

    except UserMessage.DoesNotExist:
        logging.error("Could not find UserMessage with message_id %s" % (missed_message['message_id'],))