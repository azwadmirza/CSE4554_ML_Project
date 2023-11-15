    def apiInfo(cls, url="", get={}, post={}):
        info = super(UploadedTo, cls).apiInfo(url)

        for _i in xrange(5):
            html = getURL("http://uploaded.net/api/filemultiple",
                          get={"apikey": cls.API_KEY, 'id_0': re.match(cls.__pattern__, url).group('ID')},
                          decode=True)

            if html != "can't find request":
                api = html.split(",", 4)
                if api[0] == "online":
                    info.update({'name': api[4].strip(), 'size': api[2], 'status': 2})
                else:
                    info['status'] = 1
                break
            else:
                sleep(3)

        return info