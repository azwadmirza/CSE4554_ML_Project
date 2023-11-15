    def _get_sources(self):
        server = self.config.get("server", "trollvid")
        soup = helpers.soupify(helpers.get(self.url))
        hosts = json.loads(soup.find("div", {"class":"spatry"}).previous_sibling.previous_sibling.text[21:-2])["videos"]
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