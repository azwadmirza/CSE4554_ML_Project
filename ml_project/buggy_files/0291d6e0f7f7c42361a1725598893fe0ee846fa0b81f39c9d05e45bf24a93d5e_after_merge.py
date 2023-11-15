    def parse_response(self, response):
        p, u = self.getparser()

        response_body = ''

        while True:
            data = response.read(1024)
            if not data:
                break
            response_body += native_str_to_text(data, encoding='utf-8')

        if self.verbose:
            log.info('body: %s', repr(response_body))

        # Remove SCGI headers from the response.
        _, response_body = re.split(r'\n\s*?\n', response_body, maxsplit=1)
        p.feed(response_body.encode('utf-8'))
        p.close()

        return u.close()