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
            if isinstance(v, JSON_UNFRIENDLY_TYPES):
                v = str(v)
            elif isinstance(v, me.EmbeddedDocument):
                v = json.loads(v.to_json())

            serializable_dict[k] = v

        if mask_secrets and cfg.CONF.log.mask_secrets:
            serializable_dict = self.mask_secrets(value=serializable_dict)

        return serializable_dict