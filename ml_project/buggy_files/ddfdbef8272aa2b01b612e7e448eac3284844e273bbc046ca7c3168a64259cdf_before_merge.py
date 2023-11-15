    def http_request(self, req):
        tmp_ca_cert_path, to_add_ca_cert_path, paths_checked = self.get_ca_certs()
        https_proxy = os.environ.get('https_proxy')
        context = None
        try:
            context = self._make_context(to_add_ca_cert_path)
        except Exception:
            # We'll make do with no context below
            pass

        # Detect if 'no_proxy' environment variable is set and if our URL is included
        use_proxy = self.detect_no_proxy(req.get_full_url())

        if not use_proxy:
            # ignore proxy settings for this host request
            if tmp_ca_cert_path:
                try:
                    os.remove(tmp_ca_cert_path)
                except OSError:
                    pass
            if to_add_ca_cert_path:
                try:
                    os.remove(to_add_ca_cert_path)
                except OSError:
                    pass
            return req

        try:
            if https_proxy:
                proxy_parts = generic_urlparse(urlparse(https_proxy))
                port = proxy_parts.get('port') or 443
                s = socket.create_connection((proxy_parts.get('hostname'), port))
                if proxy_parts.get('scheme') == 'http':
                    s.sendall(to_bytes(self.CONNECT_COMMAND % (self.hostname, self.port), errors='surrogate_or_strict'))
                    if proxy_parts.get('username'):
                        credentials = "%s:%s" % (proxy_parts.get('username', ''), proxy_parts.get('password', ''))
                        s.sendall(b'Proxy-Authorization: Basic %s\r\n' % base64.b64encode(to_bytes(credentials, errors='surrogate_or_strict')).strip())
                    s.sendall(b'\r\n')
                    connect_result = b""
                    while connect_result.find(b"\r\n\r\n") <= 0:
                        connect_result += s.recv(4096)
                        # 128 kilobytes of headers should be enough for everyone.
                        if len(connect_result) > 131072:
                            raise ProxyError('Proxy sent too verbose headers. Only 128KiB allowed.')
                    self.validate_proxy_response(connect_result)
                    if context:
                        ssl_s = context.wrap_socket(s, server_hostname=self.hostname)
                    elif HAS_URLLIB3_SSL_WRAP_SOCKET:
                        ssl_s = ssl_wrap_socket(s, ca_certs=tmp_ca_cert_path, cert_reqs=ssl.CERT_REQUIRED, ssl_version=PROTOCOL, server_hostname=self.hostname)
                    else:
                        ssl_s = ssl.wrap_socket(s, ca_certs=tmp_ca_cert_path, cert_reqs=ssl.CERT_REQUIRED, ssl_version=PROTOCOL)
                        match_hostname(ssl_s.getpeercert(), self.hostname)
                else:
                    raise ProxyError('Unsupported proxy scheme: %s. Currently ansible only supports HTTP proxies.' % proxy_parts.get('scheme'))
            else:
                s = socket.create_connection((self.hostname, self.port))
                if context:
                    ssl_s = context.wrap_socket(s, server_hostname=self.hostname)
                elif HAS_URLLIB3_SSL_WRAP_SOCKET:
                    ssl_s = ssl_wrap_socket(s, ca_certs=tmp_ca_cert_path, cert_reqs=ssl.CERT_REQUIRED, ssl_version=PROTOCOL, server_hostname=self.hostname)
                else:
                    ssl_s = ssl.wrap_socket(s, ca_certs=tmp_ca_cert_path, cert_reqs=ssl.CERT_REQUIRED, ssl_version=PROTOCOL)
                    match_hostname(ssl_s.getpeercert(), self.hostname)
            # close the ssl connection
            # ssl_s.unwrap()
            s.close()
        except (ssl.SSLError, CertificateError) as e:
            build_ssl_validation_error(self.hostname, self.port, paths_checked, e)
        except socket.error as e:
            raise ConnectionError('Failed to connect to %s at port %s: %s' % (self.hostname, self.port, to_native(e)))

        try:
            # cleanup the temp file created, don't worry
            # if it fails for some reason
            os.remove(tmp_ca_cert_path)
        except:
            pass

        try:
            # cleanup the temp file created, don't worry
            # if it fails for some reason
            if to_add_ca_cert_path:
                os.remove(to_add_ca_cert_path)
        except:
            pass

        return req