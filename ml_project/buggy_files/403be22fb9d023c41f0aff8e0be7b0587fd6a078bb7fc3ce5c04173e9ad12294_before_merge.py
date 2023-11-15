    def dump_map(self):
        result = dict((k, v) for k, v in iteritems(vars(self)) if not k.startswith('_'))
        result.update(exception_type=text_type(type(self)),
                      exception_name=self.__class__.__name__,
                      message=text_type(self),
                      error=repr(self),
                      caused_by=repr(self._caused_by),
                      **self._kwargs)
        return result