def shuffle(*arrays, **options):
    arrays = [convert_to_tensor_or_dataframe(ar) for ar in arrays]
    axes = options.pop('axes', (0,))
    if not isinstance(axes, Iterable):
        axes = (axes,)
    elif not isinstance(axes, tuple):
        axes = tuple(axes)
    random_state = check_random_state(
        options.pop('random_state', None)).to_numpy()
    if options:
        raise TypeError('shuffle() got an unexpected '
                        'keyword argument {0}'.format(next(iter(options))))

    max_ndim = max(ar.ndim for ar in arrays)
    axes = tuple(np.unique([validate_axis(max_ndim, ax) for ax in axes]))
    seeds = gen_random_seeds(len(axes), random_state)

    # verify shape
    for ax in axes:
        shapes = {ar.shape[ax] for ar in arrays if ax < ar.ndim}
        if len(shapes) > 1:
            raise ValueError('arrays do not have same shape on axis {0}'.format(ax))

    op = LearnShuffle(axes=axes, seeds=seeds,
                      output_types=get_output_types(*arrays))
    shuffled_arrays = op(arrays)
    if len(arrays) == 1:
        return shuffled_arrays[0]
    else:
        return ExecutableTuple(shuffled_arrays)