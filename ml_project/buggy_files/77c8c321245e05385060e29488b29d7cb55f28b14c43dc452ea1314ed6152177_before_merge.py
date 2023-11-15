                def delete_chunk(chunk):
                    resp = None
                    p = urlparse(chunk['id'])
                    try:
                        with Timeout(CHUNK_TIMEOUT):
                            conn = http_connect(p.netloc, 'DELETE', p.path)
                            resp = conn.getresponse()
                            resp.chunk = chunk
                    except (Exception, Timeout) as e:
                        self.logger.warn(
                            'error while deleting chunk %s "%s"',
                            chunk['id'], str(e.message))
                    return resp