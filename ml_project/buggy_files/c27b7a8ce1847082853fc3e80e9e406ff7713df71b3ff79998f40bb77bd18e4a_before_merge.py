def _parse_ssl_options(ssl_options):
    if ssl_options is not None:
        try:
            with open(ssl_options) as _file:
                return nginxparser.load(_file)
        except IOError:
            logger.warning("Missing NGINX TLS options file: %s", ssl_options)
        except pyparsing.ParseBaseException as err:
            logger.debug("Could not parse file: %s due to %s", ssl_options, err)
    return []