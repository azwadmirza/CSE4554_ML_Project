def with_parameters(fn, **kwargs):
    """Wrapper for function trainables to pass arbitrary large data objects.

    This wrapper function will store all passed parameters in the Ray
    object store and retrieve them when calling the function. It can thus
    be used to pass arbitrary data, even datasets, to Tune trainable functions.

    This can also be used as an alternative to `functools.partial` to pass
    default arguments to trainables.

    Args:
        fn: function to wrap
        **kwargs: parameters to store in object store.


    .. code-block:: python

        from ray import tune

        def train(config, data=None):
            for sample in data:
                # ...
                tune.report(loss=loss)

        data = HugeDataset(download=True)

        tune.run(
            tune.with_parameters(train, data=data),
            #...
        )

    """
    if not callable(fn):
        raise ValueError(
            "`tune.with_parameters()` only works with the function API. "
            "If you want to pass parameters to Trainable _classes_, consider "
            "passing them via the `config` parameter.")

    prefix = f"{str(fn)}_"
    for k, v in kwargs.items():
        parameter_registry.put(prefix + k, v)

    use_checkpoint = detect_checkpoint_function(fn)

    def inner(config, checkpoint_dir=None):
        fn_kwargs = {}
        if use_checkpoint:
            default = checkpoint_dir
            sig = inspect.signature(fn)
            if "checkpoint_dir" in sig.parameters:
                default = sig.parameters["checkpoint_dir"].default \
                          or default
            fn_kwargs["checkpoint_dir"] = default

        for k in kwargs:
            fn_kwargs[k] = parameter_registry.get(prefix + k)
        fn(config, **fn_kwargs)

    # Use correct function signature if no `checkpoint_dir` parameter is set
    if not use_checkpoint:

        def _inner(config):
            inner(config, checkpoint_dir=None)

        return _inner

    return inner