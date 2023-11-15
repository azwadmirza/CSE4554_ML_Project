    def fetch(self, segment, retries=None):
        if self.closed or not retries:
            return

        try:
            request_args = copy.deepcopy(self.reader.stream.args)
            headers = request_args.pop("headers", {})
            now = datetime.datetime.now(tz=utc)
            if segment.available_at > now:
                time_to_wait = (segment.available_at - now).total_seconds()
                fname = os.path.basename(urlparse(segment.url).path)
                log.debug("Waiting for segment: {fname} ({wait:.01f}s)".format(fname=fname, wait=time_to_wait))
                sleep_until(segment.available_at)

            if segment.range:
                start, length = segment.range
                if length:
                    end = start + length - 1
                else:
                    end = ""
                headers["Range"] = "bytes={0}-{1}".format(start, end)

            return self.session.http.get(segment.url,
                                         timeout=self.timeout,
                                         exception=StreamError,
                                         headers=headers,
                                         **request_args)
        except StreamError as err:
            log.error("Failed to open segment {0}: {1}", segment.url, err)
            return self.fetch(segment, retries - 1)