def configure_dask(data) -> Callable[[], ContextManager[dict]]:
    """Spin up cache and return context manager that optimizes Dask indexing.

    This function determines whether data is a dask array or list of dask
    arrays and prepares some optimizations if so.

    When a delayed dask array is given to napari, there are couple things that
    need to be done to optimize performance.

    1. Opportunistic caching needs to be enabled, such that we don't recompute
       (or "re-read") data that has already been computed or read.

    2. Dask task fusion must be turned off to prevent napari from triggering
       new io on data that has already been read from disk. For example, with a
       4D timelapse of 3D stacks, napari may actually *re-read* the entire 3D
       tiff file every time the Z plane index is changed. Turning of Dask task
       fusion with ``optimization.fuse.active == False`` prevents this.

       .. note::

          Turning off task fusion requires Dask version 2.15.0 or later.

    For background and context, see `napari/napari#718
    <https://github.com/napari/napari/issues/718>`_, `napari/napari#1124
    <https://github.com/napari/napari/pull/1124>`_, and `dask/dask#6084
    <https://github.com/dask/dask/pull/6084>`_.

    For details on Dask task fusion, see the documentation on `Dask
    Optimization <https://docs.dask.org/en/latest/optimize.html>`_.

    Parameters
    ----------
    data : Any
        data, as passed to a ``Layer.__init__`` method.

    Returns
    -------
    ContextManager
        A context manager that can be used to optimize dask indexing

    Examples
    --------
    >>> data = dask.array.ones((10,10,10))
    >>> optimized_slicing = configure_dask(data)
    >>> with optimized_slicing():
    ...    data[0, 2].compute()
    """
    if _is_dask_data(data):
        create_dask_cache()  # creates one if it doesn't exist
        if dask.__version__ < LooseVersion('2.15.0'):
            warnings.warn(
                'For best performance with Dask arrays in napari, please '
                'upgrade Dask to v2.15.0 or later. Current version is '
                f'{dask.__version__}'
            )

        def dask_optimized_slicing():
            with dask.config.set({"optimization.fuse.active": False}) as cfg:
                yield cfg

    else:

        def dask_optimized_slicing():
            yield {}

    return contextmanager(dask_optimized_slicing)