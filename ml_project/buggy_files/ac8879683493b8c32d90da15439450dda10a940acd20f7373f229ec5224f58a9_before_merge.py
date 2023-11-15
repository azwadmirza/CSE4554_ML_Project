    def process_request_2(self, rp, request, spider):
        if rp is not None and not rp.can_fetch(self._useragent, request.url):
            logger.debug("Forbidden by robots.txt: %(request)s",
                         {'request': request}, extra={'spider': spider})
            raise IgnoreRequest()