def iter_servers():
    for option in CONF.options('lsp-server'):
        server = LSPServer(language=option)
        server.load()
        yield server