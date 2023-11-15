    def download_request(self, request, spider):
        parsed_url = urlparse(request.url)
        creator = ClientCreator(reactor, FTPClient, request.meta["ftp_user"],
                                    request.meta["ftp_password"],
                                    passive=request.meta.get("ftp_passive", 1))
        return creator.connectTCP(parsed_url.hostname, parsed_url.port or 21).addCallback(self.gotClient,
                                request, unquote(parsed_url.path))