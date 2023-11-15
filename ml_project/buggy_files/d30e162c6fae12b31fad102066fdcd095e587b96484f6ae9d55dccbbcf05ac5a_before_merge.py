def clean_namespace(hparams):
    """Removes all functions from hparams so we can pickle."""

    if isinstance(hparams, Namespace):
        del_attrs = []
        for k in hparams.__dict__:
            if callable(getattr(hparams, k)):
                del_attrs.append(k)

        for k in del_attrs:
            delattr(hparams, k)

    elif isinstance(hparams, dict):
        del_attrs = []
        for k, v in hparams.items():
            if callable(v):
                del_attrs.append(k)

        for k in del_attrs:
            del hparams[k]