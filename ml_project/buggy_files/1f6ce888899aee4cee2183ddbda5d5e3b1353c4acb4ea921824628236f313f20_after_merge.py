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