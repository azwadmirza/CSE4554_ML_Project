def process_success_response(event: Dict[str, Any],
                             service_handler: Any,
                             response: Response) -> None:
    try:
        response_json = json.loads(response.text)
    except ValueError:
        fail_with_message(event, "Invalid JSON in response")
        return

    success_data = service_handler.process_success(response_json)

    if success_data is None:
        return

    content = success_data.get('content')

    if content is None or content.strip() == "":
        return

    widget_content = success_data.get('widget_content')
    bot_id = event['user_profile_id']
    message_info = event['message']
    response_data = dict(content=content, widget_content=widget_content)
    send_response_message(bot_id=bot_id, message_info=message_info, response_data=response_data)