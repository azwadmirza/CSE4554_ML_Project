    def getattr(self, name, context=None):
        if name == 'im_func':
            return [self._proxied]
        return self._proxied.getattr(name, context)