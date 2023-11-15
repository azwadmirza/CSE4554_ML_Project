def check_connection(server="lbry.io", port=80, timeout=2, bypass_dns=False):
    """Attempts to open a socket to server:port and returns True if successful."""
    log.debug('Checking connection to %s:%s', server, port)
    try:
        if not bypass_dns:
            server = socket.gethostbyname(server)
        socket.create_connection((server, port), timeout)
        log.debug('Connection successful')
        return True
    except (socket.gaierror, socket.herror) as ex:
        log.info("Failed to connect to %s:%s. Unable to resolve domain. Trying to bypass DNS",
                 server, port, exc_info=True)
        try:
            server = "8.8.8.8"
            port = 53
            socket.create_connection((server, port), timeout)
            log.debug('Connection successful')
            return True
        except Exception as ex:
            log.info(
                "Failed to connect to %s:%s. Maybe the internet connection is not working",
                server, port, exc_info=True)
            return False
    except Exception as ex:
        log.info(
            "Failed to connect to %s:%s. Maybe the internet connection is not working",
            server, port, exc_info=True)
        return False