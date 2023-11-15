    def run(self, *args, **kwargs):
        time.sleep(random() * self.interval)
        while True:
            pre = time.time()
            try:
                self.index_pass()
            except VolumeException as exc:
                self.logger.error('Cannot index chunks, will retry later: %s',
                                  exc)
            except Exception as exc:
                self.logger.exception('ERROR during indexing: %s', exc)
            else:
                self.passes += 1
            elapsed = (time.time() - pre) or 0.000001
            if elapsed < self.interval:
                time.sleep(self.interval - elapsed)