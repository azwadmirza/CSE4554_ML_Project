    def _parse_robots(self, response, netloc):
        rp = robotparser.RobotFileParser(response.url)
        body = ''
        if hasattr(response, 'text'):
            body = response.text
        else: # last effort try
            try:
                body = response.body.decode('utf-8')
            except UnicodeDecodeError:
                # If we found garbage, disregard it:,
                # but keep the lookup cached (in self._parsers)
                # Running rp.parse() will set rp state from
                # 'disallow all' to 'allow any'.
                pass
        rp.parse(body.splitlines())

        rp_dfd = self._parsers[netloc]
        self._parsers[netloc] = rp
        rp_dfd.callback(rp)