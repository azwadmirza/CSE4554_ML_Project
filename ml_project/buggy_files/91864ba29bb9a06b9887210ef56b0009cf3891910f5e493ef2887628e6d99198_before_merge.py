    def igetattr(self, name, context=None):
        if name == 'im_func':
            return iter((self._proxied,))
        return super(UnboundMethod, self).igetattr(name, context)