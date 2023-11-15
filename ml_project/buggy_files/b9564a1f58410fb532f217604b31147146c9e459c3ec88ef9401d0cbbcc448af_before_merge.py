def check_redaction(
    room_version_obj: RoomVersion, event: EventBase, auth_events: StateMap[EventBase],
) -> bool:
    """Check whether the event sender is allowed to redact the target event.

    Returns:
        True if the the sender is allowed to redact the target event if the
        target event was created by them.
        False if the sender is allowed to redact the target event with no
        further checks.

    Raises:
        AuthError if the event sender is definitely not allowed to redact
        the target event.
    """
    user_level = get_user_power_level(event.user_id, auth_events)

    redact_level = _get_named_level(auth_events, "redact", 50)

    if user_level >= redact_level:
        return False

    if room_version_obj.event_format == EventFormatVersions.V1:
        redacter_domain = get_domain_from_id(event.event_id)
        redactee_domain = get_domain_from_id(event.redacts)
        if redacter_domain == redactee_domain:
            return True
    else:
        event.internal_metadata.recheck_redaction = True
        return True

    raise AuthError(403, "You don't have permission to redact events")