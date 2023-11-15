    def __call__(self, name: Optional[str] = None,
                 key: Optional[Callable] = None, **kwargs) -> Any:
        """Override standard call.

        This magic method override standard call so it's take any string which
        represents name of the any method of any supported data provider
        and the ``**kwargs`` of this method.

        ..note:: Some data providers have methods with the same name and
        in such cases, you can explicitly define that the method belongs to
        data-provider ``name='provider.name'``.

        You can apply a *key function* to result returned by the method,
        to do it, just pass parameter **key** with a callable object which
        returns final result.

        :param name: Name of the method.
        :param key: A key function (or other callable object)
            which will be applied to result.
        :param kwargs: Kwargs of method.
        :return: Value which represented by method.
        :raises ValueError: if provider is not
            supported or if field is not defined.
        """
        if name is None:
            raise UndefinedField()

        def tail_parser(tails: str, obj: Any) -> Any:
            """Return method from end of tail.

            :param tails: Tail string
            :param obj: Search tail from this object
            :return last tailed method
            """
            first, second = tails.split('.', 1)
            if hasattr(obj, first):
                attr = getattr(obj, first)
                if '.' in second:
                    return tail_parser(attr, second)
                else:
                    return getattr(attr, second)

        try:
            if name not in self._table:
                if '.' not in name:
                    for provider in dir(self._gen):
                        provider = getattr(self._gen, provider)
                        if name in dir(provider):
                            self._table[name] = getattr(provider, name)
                else:
                    self._table[name] = tail_parser(name, self._gen)

            result = self._table[name](**kwargs)
            if key and callable(key):
                return key(result)
            return result
        except Exception:
            raise UnsupportedField(name)