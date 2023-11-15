async def _autodiscover_device(args, loop):
    apple_tv = await _scan_for_device(
        args, args.scan_timeout, loop, protocol=args.protocol
    )
    if not apple_tv:
        return None

    def _set_credentials(protocol, field):
        service = apple_tv.get_service(protocol)
        if service:
            value = service.credentials or getattr(args, field)
            service.credentials = value

    _set_credentials(Protocol.DMAP, "dmap_credentials")
    _set_credentials(Protocol.MRP, "mrp_credentials")
    _set_credentials(Protocol.AirPlay, "airplay_credentials")

    logging.info("Auto-discovered %s at %s", apple_tv.name, apple_tv.address)

    return apple_tv