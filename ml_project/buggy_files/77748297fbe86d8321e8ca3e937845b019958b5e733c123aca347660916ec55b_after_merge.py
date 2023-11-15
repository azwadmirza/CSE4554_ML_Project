    def _get_sources(self):
        server = self.config.get("server", "trollvid")
        resp = helpers.get(self.url).text
        hosts = json.loads(re.search("var\s+episode\s+=\s+({.*})", resp).group(1))["videos"]
        _type = hosts[0]["type"]
        try:
            host = list(filter(lambda video: video["host"] == server and video["type"] == _type, hosts))[0]
        except IndexError:
            host = hosts[0]
            if host["host"] == "mp4upload" and len(hosts) > 1:
                host = hosts[1]

        name = host["host"]
        _id = host["id"]
        link = self.getLink(name, _id)

        return [(name, link)]