    def igetattr(self, name, context=None):
        if name == 'im_func':
            return iter((self._proxied,))
        return self._proxied.igetattr(name, context)