    def masscan_post_http(self, script):
        header = re.search(re.escape('\nServer:') + '[ \\\t]*([^\\\r\\\n]+)\\\r?(?:\\\n|$)',
                           script['masscan']['raw'])
        if header is None:
            return
        header = header.groups()[0]
        self._curport.setdefault('scripts', []).append({
            "id": "http-server-header",
            "output": utils.nmap_encode_data(header),
            "masscan": {
                "raw": self._to_binary(header),
            },
        })
        self._curport['service_product'] = utils.nmap_encode_data(header)