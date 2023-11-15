    def asDict(self):
        # This return value should match the kwargs to
        # SourceStampsConnectorComponent.findSourceStampId
        result = {}
        for attr in self.ATTRS:
            result[attr] = self._ssdict.get(attr)

        patch = self._ssdict.get('patch') or {}
        for patch_attr, attr in self.PATCH_ATTRS:
            result[patch_attr] = patch.get(attr)

        assert all(
            isinstance(val, (str, int, bytes, type(None)))
            for attr, val in result.items()
        ), result
        return result