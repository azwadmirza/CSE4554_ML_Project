    def delete_chunk(self, chunk):
        resp = None
        parsed = urlparse(chunk['id'])
        try:
            with Timeout(CHUNK_TIMEOUT):
                conn = http_connect(parsed.netloc, 'DELETE', parsed.path)
                resp = conn.getresponse()
                resp.chunk = chunk
        except (Exception, Timeout) as exc:
            self.logger.warn(
                'error while deleting chunk %s "%s"',
                chunk['id'], str(exc.message))
        return resp