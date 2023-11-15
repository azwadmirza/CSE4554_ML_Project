def end():
    """Stop Glances."""
    if core.is_standalone() and not WINDOWS:
        # Stop the standalone (CLI)
        standalone.end()
        logger.info("Stop Glances (with CTRL-C)")
    elif core.is_client() and not WINDOWS:
        # Stop the client
        client.end()
        logger.info("Stop Glances client (with CTRL-C)")
    elif core.is_server():
        # Stop the server
        server.end()
        logger.info("Stop Glances server (with CTRL-C)")
    elif core.is_webserver() or (core.is_standalone() and WINDOWS):
        # Stop the Web server
        webserver.end()
        logger.info("Stop Glances web server(with CTRL-C)")

    # The end...
    sys.exit(0)