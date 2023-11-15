    def exception_to_python(self, exc):
        """Convert serialized exception to Python exception."""
        if exc:
            if not isinstance(exc, BaseException):
                exc_module = exc.get('exc_module')
                if exc_module is None:
                    cls = create_exception_cls(
                        from_utf8(exc['exc_type']), __name__)
                else:
                    exc_module = from_utf8(exc_module)
                    exc_type = from_utf8(exc['exc_type'])
                    try:
                        cls = getattr(sys.modules[exc_module], exc_type)
                    except KeyError:
                        cls = create_exception_cls(exc_type,
                                                   celery.exceptions.__name__)
                exc_msg = exc['exc_message']
                exc = cls(*exc_msg if isinstance(exc_msg, tuple) else exc_msg)
            if self.serializer in EXCEPTION_ABLE_CODECS:
                exc = get_pickled_exception(exc)
        return exc