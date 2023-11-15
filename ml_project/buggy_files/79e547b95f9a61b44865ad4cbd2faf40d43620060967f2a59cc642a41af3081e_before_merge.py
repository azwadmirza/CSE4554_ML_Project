def do_rest_call(rest_operation, request_data, event, service_handler, timeout=None):
    # type: (Dict[str, Any], Optional[Dict[str, Any]], Dict[str, Any], Any, Any) -> None
    rest_operation_validator = check_dict([
        ('method', check_string),
        ('relative_url_path', check_string),
        ('request_kwargs', check_dict([])),
        ('base_url', check_string),
    ])

    error = rest_operation_validator('rest_operation', rest_operation)
    if error:
        raise JsonableError(error)

    http_method = rest_operation['method']
    final_url = urllib.parse.urljoin(rest_operation['base_url'], rest_operation['relative_url_path'])
    request_kwargs = rest_operation['request_kwargs']
    request_kwargs['timeout'] = timeout

    try:
        response = requests.request(http_method, final_url, data=request_data, **request_kwargs)
        if str(response.status_code).startswith('2'):
            response_message = service_handler.process_success(response, event)
            if response_message is not None:
                succeed_with_message(event, response_message)
        else:
            logging.warning("Message %(message_url)s triggered an outgoing webhook, returning status "
                            "code %(status_code)s.\n Content of response (in quotes): \""
                            "%(response)s\""
                            % {'message_url': get_message_url(event, request_data),
                               'status_code': response.status_code,
                               'response': response.content})
            failure_message = "Third party responded with %d" % (response.status_code)
            fail_with_message(event, failure_message)
            notify_bot_owner(event, request_data, response.status_code, response.content)

    except requests.exceptions.Timeout:
        logging.info("Trigger event %s on %s timed out. Retrying" % (event["command"], event['service_name']))
        request_retry(event, request_data, 'Unable to connect with the third party.')

    except requests.exceptions.RequestException as e:
        response_message = "An exception occured for message `%s`! See the logs for more information." % (event["command"],)
        logging.exception("Outhook trigger failed:\n %s" % (e,))
        fail_with_message(event, response_message)
        notify_bot_owner(event, request_data, exception=e)