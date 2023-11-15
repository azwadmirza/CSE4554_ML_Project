def end():
    """Stop Glances."""
    if core.is_standalone():
        # Stop the standalone (CLI)
        standalone.end()
        logger.info("Stop Glances (with CTRL-C)")
    elif core.is_client():
        # Stop the client
        client.end()
        logger.info("Stop Glances client (with CTRL-C)")
    elif core.is_server():
        # Stop the server
        server.end()
        logger.info("Stop Glances server (with CTRL-C)")
    elif core.is_webserver():
        # Stop the Web server
        webserver.end()
        logger.info("Stop Glances web server(with CTRL-C)")

    # The end...
    sys.exit(0)