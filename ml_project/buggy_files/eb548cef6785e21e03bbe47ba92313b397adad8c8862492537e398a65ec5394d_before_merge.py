def get_external_ip_from_centralized_source(log: Logger = IP_DETECTION_LOGGER) -> Union[str, None]:
    """Use hardcoded URL to determine the external IP address of this host."""
    endpoint = 'https://ifconfig.me/'
    ip = __request(url=endpoint)
    if ip:
        log.info(f'Fetched external IP address ({ip}) from centralized source ({endpoint}).')
    return ip