    def _finger_fail(self, finger, master_key):
        log.critical(
            'The specified fingerprint in the master configuration '
            'file:\n{0}\nDoes not match the authenticating master\'s '
            'key:\n{1}\nVerify that the configured fingerprint '
            'matches the fingerprint of the correct master and that '
            'this minion is not subject to a man-in-the-middle attack.'
            .format(
                finger,
                salt.utils.pem_finger(master_key, sum_type=self.opts['hash_type'])
            )
        )
        sys.exit(42)