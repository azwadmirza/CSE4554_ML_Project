    def run(self):
        """Function called to grab stats.
        Infinite loop, should be stopped by calling the stop() method"""

        if not cloud_tag:
            logger.debug("cloud plugin - Requests lib is not installed")
            self.stop()
            return False

        for k, v in iteritems(self.AWS_EC2_API_METADATA):
            r_url = '{}/{}'.format(self.AWS_EC2_API_URL, v)
            try:
                # Local request, a timeout of 3 seconds is OK
                r = requests.get(r_url, timeout=3)
            except Exception as e:
                logger.debug('cloud plugin - Cannot connect to the AWS EC2 API {}: {}'.format(r_url, e))
                break
            else:
                if r.ok:
                    self._stats[k] = r.content

        return True