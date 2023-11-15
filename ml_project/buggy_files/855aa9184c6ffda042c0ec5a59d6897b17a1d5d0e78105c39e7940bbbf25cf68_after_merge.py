def request_retry(event, request_data, failure_message, exception=None):
    # type: (Dict[str, Any], Dict[str, Any], Text, Optional[Exception]) -> None
    def failure_processor(event):
        # type: (Dict[str, Any]) -> None
        """
        The name of the argument is 'event' on purpose. This argument will hide
        the 'event' argument of the request_retry function. Keeping the same name
        results in a smaller diff.
        """
        bot_user = get_user_profile_by_id(event['user_profile_id'])
        fail_with_message(event, "Maximum retries exceeded! " + failure_message)
        notify_bot_owner(event, request_data, exception=exception)
        logging.warning("Maximum retries exceeded for trigger:%s event:%s" % (bot_user.email, event['command']))

    retry_event('outgoing_webhooks', event, failure_processor)