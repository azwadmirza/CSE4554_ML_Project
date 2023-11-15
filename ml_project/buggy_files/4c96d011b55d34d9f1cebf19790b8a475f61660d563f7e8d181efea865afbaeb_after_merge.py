    def __call__(self, *idx, **kwds):
        """Special handling of the "()" operator for component slices.

        Creating a slice of a component returns a _IndexedComponent_slice
        object.  Subsequent attempts to call items hit this method.  We
        handle the __call__ method separately based on the item (identifier
        immediately before the "()") being called:

        - if the item was 'component', then we defer resolution of this call
        until we are actually iterating over the slice.  This allows users
        to do operations like `m.b[:].component('foo').bar[:]`

        - if the item is anything else, then we will immediately iterate over
        the slice and call the item.  This allows "vector-like" operations
        like: `m.x[:,1].fix(0)`.
        """
        # There is a weird case in pypy3.6-7.2.0 where __name__ gets
        # called after retrieving an attribute that will be called.  I
        # don't know why that happens, but we will trap it here and
        # remove the getattr(__name__) from the call stack.
        if self._call_stack[-1][0] == _IndexedComponent_slice.get_attribute \
           and self._call_stack[-1][1] == '__name__':
            self._call_stack.pop()

        self._call_stack.append( (
            _IndexedComponent_slice.call, idx, kwds ) )
        if self._call_stack[-2][1] == 'component':
            return self
        else:
            # Note: simply calling "list(self)" results in infinite
            # recursion in python2.6
            return list( i for i in self )