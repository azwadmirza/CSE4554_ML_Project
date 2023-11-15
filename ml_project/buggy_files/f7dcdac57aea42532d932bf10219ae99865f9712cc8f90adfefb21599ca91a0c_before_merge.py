def check_message(sender, client, message_type_name, message_to,
                  subject_name, message_content, realm=None, forged=False,
                  forged_timestamp=None, forwarder_user_profile=None, local_id=None,
                  sender_queue_id=None):
    # type: (UserProfile, Client, Text, Sequence[Text], Text, Text, Optional[Realm], bool, Optional[float], Optional[UserProfile], Optional[Text], Optional[Text]) -> Dict[str, Any]
    stream = None
    if not message_to and message_type_name == 'stream' and sender.default_sending_stream:
        # Use the users default stream
        message_to = [sender.default_sending_stream.name]
    elif len(message_to) == 0:
        raise JsonableError(_("Message must have recipients"))
    if len(message_content.strip()) == 0:
        raise JsonableError(_("Message must not be empty"))
    message_content = truncate_body(message_content)

    if realm is None:
        realm = sender.realm

    if message_type_name == 'stream':
        if len(message_to) > 1:
            raise JsonableError(_("Cannot send to multiple streams"))

        stream_name = message_to[0].strip()
        check_stream_name(stream_name)

        if subject_name is None:
            raise JsonableError(_("Missing topic"))
        subject = subject_name.strip()
        if subject == "":
            raise JsonableError(_("Topic can't be empty"))
        subject = truncate_topic(subject)
        ## FIXME: Commented out temporarily while we figure out what we want
        # if not valid_stream_name(subject):
        #     return json_error(_("Invalid subject name"))

        stream = get_stream(stream_name, realm)

        send_pm_if_empty_stream(sender, stream, stream_name, realm)

        if stream is None:
            raise JsonableError(_("Stream does not exist"))
        recipient = get_recipient(Recipient.STREAM, stream.id)

        if not stream.invite_only:
            # This is a public stream
            pass
        elif subscribed_to_stream(sender, stream):
            # Or it is private, but your are subscribed
            pass
        elif sender.is_api_super_user or (forwarder_user_profile is not None and
                                          forwarder_user_profile.is_api_super_user):
            # Or this request is being done on behalf of a super user
            pass
        elif sender.is_bot and subscribed_to_stream(sender.bot_owner, stream):
            # Or you're a bot and your owner is subscribed.
            pass
        else:
            # All other cases are an error.
            raise JsonableError(_("Not authorized to send to stream '%s'") % (stream.name,))

    elif message_type_name == 'private':
        mirror_message = client and client.name in ["zephyr_mirror", "irc_mirror", "jabber_mirror", "JabberMirror"]
        not_forged_mirror_message = mirror_message and not forged
        try:
            recipient = recipient_for_emails(message_to, not_forged_mirror_message,
                                             forwarder_user_profile, sender)
        except ValidationError as e:
            assert isinstance(e.messages[0], six.string_types)
            raise JsonableError(e.messages[0])
    else:
        raise JsonableError(_("Invalid message type"))

    message = Message()
    message.sender = sender
    message.content = message_content
    message.recipient = recipient
    if message_type_name == 'stream':
        message.subject = subject
    if forged and forged_timestamp is not None:
        # Forged messages come with a timestamp
        message.pub_date = timestamp_to_datetime(forged_timestamp)
    else:
        message.pub_date = timezone.now()
    message.sending_client = client

    # We render messages later in the process.
    assert message.rendered_content is None

    if client.name == "zephyr_mirror":
        id = already_sent_mirrored_message_id(message)
        if id is not None:
            return {'message': id}

    return {'message': message, 'stream': stream, 'local_id': local_id, 'sender_queue_id': sender_queue_id}