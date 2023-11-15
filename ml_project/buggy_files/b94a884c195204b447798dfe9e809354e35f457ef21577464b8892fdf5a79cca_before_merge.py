def listen():
    reactor.listenTCP(9050, socks.SOCKSv5Factory())
    for i, key in enumerate(_get_service_keys(os.environ)):
        host = os.environ[key]
        port = int(os.environ[key[:-4] + "PORT"])
        service = endpoints.TCP4ServerEndpoint(reactor, 2000 + i)
        service.listen(ProxyFactory(host, port))
        print(
            "Connecting port {} to {}:{} ({})".
            format(2000 + i, host, port, key)
        )