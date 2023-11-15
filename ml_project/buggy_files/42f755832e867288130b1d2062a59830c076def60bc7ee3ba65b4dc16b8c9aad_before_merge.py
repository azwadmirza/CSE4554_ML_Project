def init():
    logger = logging.getLogger(__name__)
    global __HTTP
    proxy_url = os.getenv("http_proxy")
    if proxy_url and len(proxy_url) > 0:
        logger.info("Rally connects via proxy URL [%s] to the Internet (picked up from the environment variable [http_proxy]).",  proxy_url)
        __HTTP = urllib3.ProxyManager(proxy_url, cert_reqs='CERT_REQUIRED', ca_certs=certifi.where())
    else:
        logger.info("Rally connects directly to the Internet (no proxy support).")
        __HTTP = urllib3.PoolManager(cert_reqs='CERT_REQUIRED', ca_certs=certifi.where())