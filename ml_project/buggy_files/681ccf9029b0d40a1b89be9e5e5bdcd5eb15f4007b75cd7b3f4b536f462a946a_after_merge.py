def _serialize_payload(
    payload: dict, use_msgpack: Optional[bool] = False
) -> Union[bytes, str]:
    logger.debug(f"Serializing to msgpack: {use_msgpack}")
    if use_msgpack:
        return msgpack.dumps(payload, default=json_iso_dttm_ser, use_bin_type=True)
    else:
        return json.dumps(payload, default=json_iso_dttm_ser, ignore_nan=True)