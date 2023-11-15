def _check_sigs_on_pdus(
    keyring: Keyring, room_version: str, pdus: Iterable[EventBase]
) -> List[Deferred]:
    """Check that the given events are correctly signed

    Args:
        keyring: keyring object to do the checks
        room_version: the room version of the PDUs
        pdus: the events to be checked

    Returns:
        A Deferred for each event in pdus, which will either succeed if
           the signatures are valid, or fail (with a SynapseError) if not.
    """

    # we want to check that the event is signed by:
    #
    # (a) the sender's server
    #
    #     - except in the case of invites created from a 3pid invite, which are exempt
    #     from this check, because the sender has to match that of the original 3pid
    #     invite, but the event may come from a different HS, for reasons that I don't
    #     entirely grok (why do the senders have to match? and if they do, why doesn't the
    #     joining server ask the inviting server to do the switcheroo with
    #     exchange_third_party_invite?).
    #
    #     That's pretty awful, since redacting such an invite will render it invalid
    #     (because it will then look like a regular invite without a valid signature),
    #     and signatures are *supposed* to be valid whether or not an event has been
    #     redacted. But this isn't the worst of the ways that 3pid invites are broken.
    #
    # (b) for V1 and V2 rooms, the server which created the event_id
    #
    # let's start by getting the domain for each pdu, and flattening the event back
    # to JSON.

    pdus_to_check = [
        PduToCheckSig(
            pdu=p,
            redacted_pdu_json=prune_event(p).get_pdu_json(),
            sender_domain=get_domain_from_id(p.sender),
            deferreds=[],
        )
        for p in pdus
    ]

    v = KNOWN_ROOM_VERSIONS.get(room_version)
    if not v:
        raise RuntimeError("Unrecognized room version %s" % (room_version,))

    # First we check that the sender event is signed by the sender's domain
    # (except if its a 3pid invite, in which case it may be sent by any server)
    pdus_to_check_sender = [p for p in pdus_to_check if not _is_invite_via_3pid(p.pdu)]

    more_deferreds = keyring.verify_json_objects_for_server(
        [
            (
                p.sender_domain,
                p.redacted_pdu_json,
                p.pdu.origin_server_ts if v.enforce_key_validity else 0,
                p.pdu.event_id,
            )
            for p in pdus_to_check_sender
        ]
    )

    def sender_err(e, pdu_to_check):
        errmsg = "event id %s: unable to verify signature for sender %s: %s" % (
            pdu_to_check.pdu.event_id,
            pdu_to_check.sender_domain,
            e.getErrorMessage(),
        )
        raise SynapseError(403, errmsg, Codes.FORBIDDEN)

    for p, d in zip(pdus_to_check_sender, more_deferreds):
        d.addErrback(sender_err, p)
        p.deferreds.append(d)

    # now let's look for events where the sender's domain is different to the
    # event id's domain (normally only the case for joins/leaves), and add additional
    # checks. Only do this if the room version has a concept of event ID domain
    # (ie, the room version uses old-style non-hash event IDs).
    if v.event_format == EventFormatVersions.V1:
        pdus_to_check_event_id = [
            p
            for p in pdus_to_check
            if p.sender_domain != get_domain_from_id(p.pdu.event_id)
        ]

        more_deferreds = keyring.verify_json_objects_for_server(
            [
                (
                    get_domain_from_id(p.pdu.event_id),
                    p.redacted_pdu_json,
                    p.pdu.origin_server_ts if v.enforce_key_validity else 0,
                    p.pdu.event_id,
                )
                for p in pdus_to_check_event_id
            ]
        )

        def event_err(e, pdu_to_check):
            errmsg = (
                "event id %s: unable to verify signature for event id domain: %s"
                % (pdu_to_check.pdu.event_id, e.getErrorMessage())
            )
            raise SynapseError(403, errmsg, Codes.FORBIDDEN)

        for p, d in zip(pdus_to_check_event_id, more_deferreds):
            d.addErrback(event_err, p)
            p.deferreds.append(d)

    # replace lists of deferreds with single Deferreds
    return [_flatten_deferred_list(p.deferreds) for p in pdus_to_check]