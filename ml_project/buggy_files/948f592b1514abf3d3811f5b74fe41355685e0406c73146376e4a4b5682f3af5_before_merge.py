    def _get_sources(self):
        server = self.config.get("server", "trollvid")
        soup = helpers.soupify(helpers.get(self.url))
        hosts = json.loads(soup.find("div", {"class":"col-sm-9"}).find("script").text[30:-6])
        _type = hosts[0]["type"]
        try:
            host = list(filter(lambda video: video["host"] == server and video["type"] == _type, hosts))[0]
        except IndexError:
            host = hosts[0]
            #I will try to avoid mp4upload since it mostly doesn't work
            if host["host"] == "mp4upload" and len(hosts) > 1:
                host = hosts[1]

        name = host["host"]
        _id = host["id"]
        link = self.getLink(name, _id)

        return [(name, link)]