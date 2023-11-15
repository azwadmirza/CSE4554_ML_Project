def parse_services(message: DnsMessage) -> typing.List[Service]:
    """Parse DNS response into Service objects."""
    table: typing.Dict[str, typing.Dict[int, DnsResource]] = {}
    ptrs: typing.Dict[str, str] = {}  # qname -> real name
    results: typing.Dict[str, Service] = {}

    # Create a global table with all records
    for record in message.answers + message.resources:
        if record.qtype == QueryType.PTR and record.qname.startswith("_"):
            ptrs[record.qname] = record.rd
        else:
            table.setdefault(record.qname, {})[record.qtype] = record

    # Build services
    for service, device in table.items():
        service_name, _, service_type = service.partition(".")

        if not service_type.endswith("_tcp.local"):
            continue

        port = (QueryType.SRV in device and device[QueryType.SRV].rd["port"]) or 0
        target = (
            QueryType.SRV in device and device[QueryType.SRV].rd["target"]
        ) or None
        properties = (QueryType.TXT in device and device[QueryType.TXT].rd) or {}

        target_record = table.get(typing.cast(str, target), {}).get(QueryType.A)
        address = IPv4Address(target_record.rd) if target_record else None

        results[service] = Service(
            service_type,
            service_name,
            address,
            port,
            _decode_properties(properties),
        )

    # If there are PTRs to unknown services, create placeholders
    for qname, real_name in ptrs.items():
        if real_name not in results:
            results[real_name] = Service(qname, real_name.split(".")[0], None, 0, {})

    return list(results.values())