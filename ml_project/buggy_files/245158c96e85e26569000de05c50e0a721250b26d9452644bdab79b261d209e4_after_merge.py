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
            except VolumeException as exc:
                self.errors += 1
                self.logger.error('Cannot index %s: %s', path, exc)
                # All chunks of this volume are indexed in the same service,
                # no need to try another chunk, it will generate the same
                # error. Let the upper level retry later.
                raise
            except Exception:
                self.errors += 1
                self.logger.exception('ERROR while updating %s', path)
            self.total_since_last_reported += 1