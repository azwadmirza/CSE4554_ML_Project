def get_external_ip_from_known_nodes(known_nodes: FleetSensor,
                                     sample_size: int = 3,
                                     log: Logger = IP_DETECTION_LOGGER
                                     ) -> Union[str, None]:
    """
    Randomly select a sample of peers to determine the external IP address
    of this host. The first node to reply successfully will be used.
    # TODO: Parallelize the requests and compare results.
    """
    ip = None
    sample = random.sample(known_nodes, sample_size)
    for node in sample:
        ip = __request(url=node.rest_url())
        if ip:
            log.info(f'Fetched external IP address ({ip}) from randomly selected known node(s).')
            return ip