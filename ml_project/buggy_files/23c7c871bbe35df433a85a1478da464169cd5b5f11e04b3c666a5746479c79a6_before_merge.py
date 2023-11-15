    def getattr(self, name, context=None):
        if name == 'im_func':
            return [self._proxied]
        return super(UnboundMethod, self).getattr(name, context)