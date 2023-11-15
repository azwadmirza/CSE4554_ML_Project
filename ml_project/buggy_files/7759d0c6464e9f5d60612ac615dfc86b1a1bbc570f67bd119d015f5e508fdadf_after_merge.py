def getter_with_load_details(name: str, type: Union[str, type]) -> Callable:
    """
    :note: confirm that the type annotation `get_foo = getter_with_load_details("_foo", type=int)  # type: Callable[..., int]` is correct one
    :note: this cannot be a decorator, since mypy fails to recognize the types

    This functions is bad one, but I think

        get_foo = getter_with_load_details("_foo", type=int)  # type: Callable[..., int]

    is better than

        def get_foo(self, session: Optional[requests.Session] = None) -> int:
            if self._foo is None:
                self._load_details(session=session)
                assert self._foo is not None
            return self._foo

    Of course the latter is better when it is used only once, but the former is better when the pattern is repeated.
    """

    @functools.wraps(lambda self: getattr(self, name))
    def wrapper(self, session: Optional[requests.Session] = None):
        if getattr(self, name) is None:
            assert session is None or isinstance(session, requests.Session)
            self._load_details(session=session)
        return getattr(self, name)

    # add documents
    assert type is not None
    py_class = lambda s: ':py:class:`{}`'.format(s)
    if isinstance(type, str):
        if type.count('[') == 0:
            rst = py_class(type)
        elif type.count('[') == 1:
            a, b = remove_suffix(type, ']').split('[')
            rst = '{} [ {} ]'.format(py_class(a), py_class(b))
        else:
            assert False
    elif type in (int, float, str, bytes, datetime.datetime, datetime.timedelta):
        rst = py_class(type.__name__)
    else:
        assert False
    wrapper.__doc__ = ':return: {}'.format(rst)

    return wrapper