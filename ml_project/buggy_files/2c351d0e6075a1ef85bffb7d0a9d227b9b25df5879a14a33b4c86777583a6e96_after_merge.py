def get_external_ip_from_known_nodes(known_nodes: FleetSensor,
                                     sample_size: int = 3,
                                     log: Logger = IP_DETECTION_LOGGER
                                     ) -> Union[str, None]:
    """
    Randomly select a sample of peers to determine the external IP address
    of this host. The first node to reply successfully will be used.
    # TODO: Parallelize the requests and compare results.
    """
    if len(known_nodes) < sample_size:
        return  # There are too few known nodes
    sample = random.sample(list(known_nodes), sample_size)
    client = NucypherMiddlewareClient()
    for node in sample:
        ip = _request_from_node(teacher=node, client=client)
        if ip:
            log.info(f'Fetched external IP address ({ip}) from randomly selected known nodes.')
            return ip