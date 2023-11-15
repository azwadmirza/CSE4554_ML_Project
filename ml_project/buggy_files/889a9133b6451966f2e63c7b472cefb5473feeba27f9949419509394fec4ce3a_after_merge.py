def _is_invite_via_3pid(event: EventBase) -> bool:
    return (
        event.type == EventTypes.Member
        and event.membership == Membership.INVITE
        and "third_party_invite" in event.content
    )