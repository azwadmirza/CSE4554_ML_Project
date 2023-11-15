def create_worker(
    func: Callable,
    *args,
    _start_thread: Optional[bool] = None,
    _connect: Optional[Dict[str, Union[Callable, Sequence[Callable]]]] = None,
    _worker_class: Optional[Type[WorkerBase]] = None,
    _ignore_errors: bool = False,
    **kwargs,
) -> WorkerBase:
    """Convenience function to start a function in another thread.

    By default, uses :class:`Worker`, but a custom ``WorkerBase`` subclass may
    be provided.  If so, it must be a subclass of :class:`Worker`, which
    defines a standard set of signals and a run method.

    Parameters
    ----------
    func : Callable
        The function to call in another thread.
    _start_thread : bool, optional
        Whether to immediaetly start the thread.  If False, the returned worker
        must be manually started with ``worker.start()``. by default it will be
        ``False`` if the ``_connect`` argument is ``None``, otherwise ``True``.
    _connect : Dict[str, Union[Callable, Sequence]], optional
        A mapping of ``"signal_name"`` -> ``callable`` or list of ``callable``:
        callback functions to connect to the various signals offered by the
        worker class. by default None
    _worker_class : Type[WorkerBase], optional
        The :class`WorkerBase` to instantiate, by default
        :class:`FunctionWorker` will be used if ``func`` is a regular function,
        and :class:`GeneratorWorker` will be used if it is a generator.
    _ignore_errors : bool, optional
        If ``False`` (the default), errors raised in the other thread will be
        reraised in the main thread (makes debugging significantly easier).
    *args
        will be passed to ``func``
    **kwargs
        will be passed to ``func``

    Returns
    -------
    worker : WorkerBase
        An instantiated worker.  If ``_start_thread`` was ``False``, the worker
        will have a `.start()` method that can be used to start the thread.

    Raises
    ------
    TypeError
        If a worker_class is provided that is not a subclass of WorkerBase.
    TypeError
        If _connect is provided and is not a dict of ``{str: callable}``

    Examples
    --------

    .. code-block:: python

        def long_function(duration):
            import time
            time.sleep(duration)

        worker = create_worker(long_function, 10)

    """
    if not _worker_class:
        if inspect.isgeneratorfunction(func):
            _worker_class = GeneratorWorker
        else:
            _worker_class = FunctionWorker

    if not (
        inspect.isclass(_worker_class)
        and issubclass(_worker_class, WorkerBase)
    ):
        raise TypeError(
            f'Worker {_worker_class} must be a subclass of WorkerBase'
        )

    worker = _worker_class(func, *args, **kwargs)

    if _connect is not None:
        if not isinstance(_connect, dict):
            raise TypeError("The '_connect' argument must be a dict")

        if _start_thread is None:
            _start_thread = True

        for key, val in _connect.items():
            _val = val if isinstance(val, (tuple, list)) else [val]
            for v in _val:
                if not callable(v):
                    raise TypeError(
                        f'"_connect[{key!r}]" must be a function or '
                        'sequence of functions'
                    )
                getattr(worker, key).connect(v)

    # if the user has not provided a default connection for the "errored"
    # signal... and they have not explicitly set ``ignore_errors=True``
    # Then rereaise any errors from the thread.
    if not _ignore_errors and not (_connect or {}).get('errored', False):

        def reraise(e):
            raise e

        worker.errored.connect(reraise)

    if _start_thread:
        worker.start()
    return worker