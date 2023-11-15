def unpack_callback_protocol(t: Instance) -> Optional[Type]:
    assert t.type.is_protocol
    if t.type.protocol_members == ['__call__']:
        return find_member('__call__', t, t, is_operator=True)
    return None