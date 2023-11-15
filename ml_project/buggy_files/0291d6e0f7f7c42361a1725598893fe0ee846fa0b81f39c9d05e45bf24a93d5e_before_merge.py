    def parse_response(self, response):
        p, u = self.getparser()

        response_body = ''

        while True:
            data = response.read(1024)
            if not data:
                break
            response_body += data

        if self.verbose:
            log.info('body: %s', repr(response_body))

        # Remove SCGI headers from the response.
        _, response_body = re.split(r'\n\s*?\n', response_body, maxsplit=1)
        p.feed(response_body)
        p.close()

        return u.close()