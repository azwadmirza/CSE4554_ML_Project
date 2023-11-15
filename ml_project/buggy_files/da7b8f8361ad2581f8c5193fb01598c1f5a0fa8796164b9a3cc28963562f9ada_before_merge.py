    def index_pass(self):

        def safe_update_index(path):
            chunk_id = path.rsplit('/', 1)[-1]
            if len(chunk_id) != STRLEN_CHUNKID:
                return
            for c in chunk_id:
                if c not in hexdigits:
                    return
            try:
                self.update_index(path)
                self.successes += 1
                self.logger.debug('Updated %s', path)
            except OioNetworkException as exc:
                self.errors += 1
                self.logger.warn('ERROR while updating %s: %s', path, exc)
            except Exception:
                self.errors += 1
                self.logger.exception('ERROR while updating %s', path)
            self.total_since_last_reported += 1

        def report(tag):
            total = self.errors + self.successes
            now = time.time()
            elapsed = (now - start_time) or 0.000001
            self.logger.info(
                '%(tag)s=%(current_time)s '
                'elapsed=%(elapsed).02f '
                'pass=%(pass)d '
                'errors=%(errors)d '
                'chunks=%(nb_chunks)d %(c_rate).2f/s' % {
                    'tag': tag,
                    'current_time': datetime.fromtimestamp(
                        int(now)).isoformat(),
                    'pass': self.passes,
                    'errors': self.errors,
                    'nb_chunks': total,
                    'c_rate': self.total_since_last_reported /
                    (now - self.last_reported),
                    'elapsed': elapsed
                }
            )
            self.last_reported = now
            self.total_since_last_reported = 0

        start_time = time.time()
        self.last_reported = start_time
        self.errors = 0
        self.successes = 0

        paths = paths_gen(self.volume)
        report('started')
        for path in paths:
            safe_update_index(path)
            self.chunks_run_time = ratelimit(
                self.chunks_run_time,
                self.max_chunks_per_second
            )
            now = time.time()
            if now - self.last_reported >= self.report_interval:
                report('running')
        report('ended')