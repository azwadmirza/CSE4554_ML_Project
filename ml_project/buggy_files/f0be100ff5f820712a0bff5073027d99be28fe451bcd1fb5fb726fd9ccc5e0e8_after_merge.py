def build_bcm_header(
    opcode,
    flags,
    count,
    ival1_seconds,
    ival1_usec,
    ival2_seconds,
    ival2_usec,
    can_id,
    nframes,
):
    result = BcmMsgHead(
        opcode=opcode,
        flags=flags,
        count=count,
        ival1_tv_sec=ival1_seconds,
        ival1_tv_usec=ival1_usec,
        ival2_tv_sec=ival2_seconds,
        ival2_tv_usec=ival2_usec,
        can_id=can_id,
        nframes=nframes,
    )
    return ctypes.string_at(ctypes.addressof(result), ctypes.sizeof(result))