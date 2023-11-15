    def _timeout_inquiries(self):
        """Mark Inquiries as "timeout" that have exceeded their TTL
        """
        try:
            purge_inquiries(logger=LOG)
        except Exception as e:
            LOG.exception('Failed to purge inquiries: %s' % (six.text_type(e)))

        return True