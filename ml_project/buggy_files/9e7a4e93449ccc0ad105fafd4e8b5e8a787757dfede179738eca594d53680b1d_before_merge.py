      def wait_for_run_completion(self, timeout=None):
        timeout = timeout or datetime.datetime.max - datetime.datetime.min
        return self._client.wait_for_run_completion(self.run_id, timeout)