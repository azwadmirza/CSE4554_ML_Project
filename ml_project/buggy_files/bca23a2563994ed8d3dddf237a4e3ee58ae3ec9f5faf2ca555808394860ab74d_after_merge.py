def batching_multi_input(func: Callable[[Any], np.ndarray] = None,
                         batch_size: Union[int, Callable] = None,
                         num_batch: Optional[int] = None,
                         split_over_axis: int = 0,
                         merge_over_axis: int = 0,
                         slice_on: int = 1,
                         num_data: int = 1) -> Any:
    """Split the input of a function into small batches and call :func:`func` on each batch
    , collect the merged result and return. This is useful when the input is too big to fit into memory

    :param func: function to decorate
    :param batch_size: size of each batch
    :param num_batch: number of batches to take, the rest will be ignored
    :param split_over_axis: split over which axis into batches
    :param merge_over_axis: merge over which axis into a single result
    :param slice_on: the location of the data. When using inside a class,
            ``slice_on`` should take ``self`` into consideration.
    :param num_data: the number of data inside the arguments
    :return: the merged result as if run :func:`func` once on the input.

    ..warning:
        data arguments will be taken starting from ``slice_on` to ``slice_on + num_data``

    Example:
        .. highlight:: python
        .. code-block:: python

            class MultiModalExecutor:

                @batching_multi_input(batch_size = 64, num_data=2)
                def encode(self, *batches, **kwargs):
                    batch_modality0 = batches[0]
                    embed0 = _encode_modality(batch_modality0)
                    batch_modality1 = batches[1]
                    embed1 = _encode_modality(batch_modality0)
    """

    def _batching(func):
        @wraps(func)
        def arg_wrapper(*args, **kwargs):
            data = args[slice_on]
            # priority: decorator > class_attribute
            # by default data is in args[1:] (self needs to be taken into account)
            b_size = batch_size or getattr(args[0], 'batch_size', None)
            # no batching if b_size is None
            if b_size is None or data is None:
                return func(*args, **kwargs)

            args = list(args)
            default_logger.debug(
                f'batching enabled for {func.__qualname__} batch_size={b_size} '
                f'num_batch={num_batch} axis={split_over_axis}')

            # assume all datas have the same length
            full_data_size = _get_size(args[slice_on], split_over_axis)
            total_size = _get_total_size(full_data_size, b_size, num_batch)
            final_result = []
            data_iterators = [batch_iterator(args[slice_on + i][:total_size], b_size, split_over_axis) for i in
                              range(0, num_data)]

            for batch in data_iterators[0]:
                args[slice_on] = batch
                for idx in range(1, num_data):
                    args[slice_on + idx] = next(data_iterators[idx])

                r = func(*args, **kwargs)

                if r is not None:
                    final_result.append(r)

            return _merge_results_after_batching(final_result, merge_over_axis)

        return arg_wrapper

    if func:
        return _batching(func)
    else:
        return _batching