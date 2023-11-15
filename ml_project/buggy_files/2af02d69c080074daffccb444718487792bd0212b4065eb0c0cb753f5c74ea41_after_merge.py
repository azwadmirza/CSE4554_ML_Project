def iter_servers():
    for option in CONF.options('lsp-server'):
        if option in [l.lower() for l in LSP_LANGUAGES]:
            server = LSPServer(language=option)
            server.load()
            yield server