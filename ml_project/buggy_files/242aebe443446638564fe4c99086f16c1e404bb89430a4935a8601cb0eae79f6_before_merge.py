def process_message(message: message.Message, rcpt_to: Optional[Text]=None, pre_checked: bool=False) -> None:
    subject_header = message.get("Subject", "(no subject)")
    encoded_subject, encoding = decode_header(subject_header)[0]
    if encoding is None:
        subject = force_text(encoded_subject)  # encoded_subject has type str when encoding is None
    else:
        try:
            subject = encoded_subject.decode(encoding)
        except (UnicodeDecodeError, LookupError):
            subject = "(unreadable subject)"

    debug_info = {}

    try:
        if rcpt_to is not None:
            to = rcpt_to
        else:
            to = find_emailgateway_recipient(message)
        debug_info["to"] = to

        if is_missed_message_address(to):
            process_missed_message(to, message, pre_checked)
        else:
            process_stream_message(to, subject, message, debug_info)
    except ZulipEmailForwardError as e:
        # TODO: notify sender of error, retry if appropriate.
        log_and_report(message, str(e), debug_info)