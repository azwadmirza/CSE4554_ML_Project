    def to_serializable_dict(self, mask_secrets=False):
        """
        Serialize database model to a dictionary.

        :param mask_secrets: True to mask secrets in the resulting dict.
        :type mask_secrets: ``boolean``

        :rtype: ``dict``
        """
        serializable_dict = {}
        for k in sorted(six.iterkeys(self._fields)):
            v = getattr(self, k)
            v = str(v) if isinstance(v, JSON_UNFRIENDLY_TYPES) else v
            serializable_dict[k] = v

        if mask_secrets and cfg.CONF.log.mask_secrets:
            serializable_dict = self.mask_secrets(value=serializable_dict)

        return serializable_dict