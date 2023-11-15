def init():
    logger = logging.getLogger(__name__)
    global __HTTP
    proxy_url = os.getenv("http_proxy")
    if proxy_url and len(proxy_url) > 0:
        parsed_url = urllib3.util.parse_url(proxy_url)
        logger.info("Connecting via proxy URL [%s] to the Internet (picked up from the env variable [http_proxy]).",
                    proxy_url)
        __HTTP = urllib3.ProxyManager(proxy_url,
                                      cert_reqs='CERT_REQUIRED',
                                      ca_certs=certifi.where(),
                                      # appropriate headers will only be set if there is auth info
                                      proxy_headers=urllib3.make_headers(proxy_basic_auth=parsed_url.auth))
    else:
        logger.info("Connecting directly to the Internet (no proxy support).")
        __HTTP = urllib3.PoolManager(cert_reqs='CERT_REQUIRED', ca_certs=certifi.where())