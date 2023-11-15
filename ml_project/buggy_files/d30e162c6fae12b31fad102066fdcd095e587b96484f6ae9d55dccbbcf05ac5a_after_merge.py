def clean_namespace(hparams):
    """Removes all unpicklable entries from hparams"""

    hparams_dict = hparams
    if isinstance(hparams, Namespace):
        hparams_dict = hparams.__dict__

    del_attrs = [k for k, v in hparams_dict.items() if not is_picklable(v)]

    for k in del_attrs:
        rank_zero_warn(f"attribute '{k}' removed from hparams because it cannot be pickled", UserWarning)
        del hparams_dict[k]