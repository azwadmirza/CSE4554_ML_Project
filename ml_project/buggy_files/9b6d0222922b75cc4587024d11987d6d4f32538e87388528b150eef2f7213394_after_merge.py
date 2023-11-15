        def set_proxy(self, host):
            self.proxy = urlparse(host)
            if not self.proxy.hostname:
                # User omitted scheme from the proxy; assume http
                self.proxy = urlparse('http://'+proxy)