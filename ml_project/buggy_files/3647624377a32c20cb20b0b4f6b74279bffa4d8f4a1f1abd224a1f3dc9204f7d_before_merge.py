def send_response_message(bot_id: str, message_info: Dict[str, Any], response_data: Dict[str, Any]) -> None:
    """
    bot_id is the user_id of the bot sending the response

    message_info is used to address the message and should have these fields:
        type - "stream" or "private"
        display_recipient - like we have in other message events
        topic - see get_topic_from_message_info

    response_data is what the bot wants to send back and has these fields:
        content - raw markdown content for Zulip to render
    """

    message_type = message_info['type']
    display_recipient = message_info['display_recipient']
    try:
        topic_name = get_topic_from_message_info(message_info)
    except KeyError:
        topic_name = None

    bot_user = get_user_profile_by_id(bot_id)
    realm = bot_user.realm
    client = get_client('OutgoingWebhookResponse')

    content = response_data.get('content')
    if not content:
        raise JsonableError(_("Missing content"))

    widget_content = response_data.get('widget_content')

    if message_type == 'stream':
        message_to = [display_recipient]
    elif message_type == 'private':
        message_to = [recipient['email'] for recipient in display_recipient]
    else:
        raise JsonableError(_("Invalid message type"))

    check_send_message(
        sender=bot_user,
        client=client,
        message_type_name=message_type,
        message_to=message_to,
        topic_name=topic_name,
        message_content=content,
        widget_content=widget_content,
        realm=realm,
    )