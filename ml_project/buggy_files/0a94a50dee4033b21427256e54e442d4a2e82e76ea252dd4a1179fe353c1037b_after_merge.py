        def _encode_host(cls, host):
            try:
                ip, sep, zone = host.partition("%")
                ip = ip_address(ip)
            except ValueError:
                for char in host:
                    if char > "\x7f":
                        break
                else:
                    return host
                try:
                    host = idna.encode(host, uts46=True).decode("ascii")
                except UnicodeError:
                    host = host.encode("idna").decode("ascii")
            else:
                host = ip.compressed
                if sep:
                    host += "%" + zone
                if ip.version == 6:
                    host = "[" + host + "]"
            return host