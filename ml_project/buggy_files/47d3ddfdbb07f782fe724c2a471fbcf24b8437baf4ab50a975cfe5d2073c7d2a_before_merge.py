async def request(
    loop: asyncio.AbstractEventLoop,
    address: str,
    services: List[str],
    port: int = 5353,
    timeout: int = 4,
):
    """Send request for services to a host."""
    if not net.get_local_address_reaching(IPv4Address(address)):
        raise exceptions.NonLocalSubnetError(
            f"address {address} is not in any local subnet"
        )

    transport, protocol = await loop.create_datagram_endpoint(
        lambda: UnicastDnsSdClientProtocol(loop, services, address),
        remote_addr=(address, port),
    )

    try:

        return await cast(UnicastDnsSdClientProtocol, protocol).get_response(timeout)
    finally:
        transport.close()