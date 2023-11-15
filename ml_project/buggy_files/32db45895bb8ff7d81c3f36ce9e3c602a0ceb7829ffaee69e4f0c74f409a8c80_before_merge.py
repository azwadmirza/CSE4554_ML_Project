        def arg_wrapper(*args, **kwargs):
            # priority: decorator > class_attribute
            # by default data is in args[1] (self needs to be taken into account)
            data = args[slice_on]
            args = list(args)

            b_size = (batch_size(data) if callable(batch_size) else batch_size) or getattr(args[0], 'batch_size', None)
            # no batching if b_size is None
            if b_size is None:
                return func(*args, **kwargs)

            default_logger.debug(
                f'batching enabled for {func.__qualname__} batch_size={b_size} '
                f'num_batch={num_batch} axis={split_over_axis}')

            full_data_size = _get_size(data, split_over_axis)
            total_size = _get_total_size(full_data_size, batch_size, num_batch)

            final_result = []

            data = (data, args[label_on]) if label_on else data

            yield_slice = isinstance(data, np.memmap)
            slice_idx = None

            for b in batch_iterator(data[:total_size], b_size, split_over_axis, yield_slice=yield_slice):
                if yield_slice:
                    slice_idx = b
                    new_memmap = np.memmap(data.filename, dtype=data.dtype, mode='r', shape=data.shape)
                    b = new_memmap[slice_idx]
                    slice_idx = slice_idx[split_over_axis]
                    if slice_idx.start is None or slice_idx.stop is None:
                        slice_idx = None

                if not isinstance(b, tuple):
                    # for now, keeping ordered_idx is only supported if no labels
                    args[slice_on] = b
                    if ordinal_idx_arg and slice_idx is not None:
                        args[ordinal_idx_arg] = slice_idx
                else:
                    args[slice_on] = b[0]
                    args[label_on] = b[1]

                r = func(*args, **kwargs)

                if yield_slice:
                    del new_memmap

                if r is not None:
                    final_result.append(r)

            return _merge_results_after_batching(final_result, merge_over_axis)