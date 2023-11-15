    def _apply_wildcards(
        self,
        newitems,
        olditems,
        wildcards,
        concretize=None,
        check_return_type=True,
        omit_callable=False,
        mapping=None,
        no_flattening=False,
        aux_params=None,
        apply_default_remote=True,
        incomplete_checkpoint_func=lambda e: None,
        allow_unpack=True,
    ):
        if aux_params is None:
            aux_params = dict()
        for name, item in olditems.allitems():
            start = len(newitems)
            is_unpack = is_flagged(item, "unpack")
            _is_callable = is_callable(item)

            if _is_callable:
                if omit_callable:
                    continue
                item, incomplete = self.apply_input_function(
                    item,
                    wildcards,
                    incomplete_checkpoint_func=incomplete_checkpoint_func,
                    is_unpack=is_unpack,
                    **aux_params
                )
                if apply_default_remote:
                    item = self.apply_default_remote(item)

            if is_unpack and not incomplete:
                if not allow_unpack:
                    raise WorkflowError(
                        "unpack() is not allowed with params. "
                        "Simply return a dictionary which can be directly ."
                        "used, e.g. via {params[mykey]}."
                    )
                # Sanity checks before interpreting unpack()
                if not isinstance(item, (list, dict)):
                    raise WorkflowError(
                        "Can only use unpack() on list and dict", rule=self
                    )
                if name:
                    raise WorkflowError(
                        "Cannot combine named input file with unpack()", rule=self
                    )
                # Allow streamlined code with/without unpack
                if isinstance(item, list):
                    pairs = zip([None] * len(item), item)
                else:
                    assert isinstance(item, dict)
                    pairs = item.items()
            else:
                pairs = [(name, item)]

            for name, item in pairs:
                is_iterable = True
                if not_iterable(item) or no_flattening:
                    item = [item]
                    is_iterable = False
                for item_ in item:
                    if check_return_type and not isinstance(item_, str):
                        raise WorkflowError(
                            "Function did not return str or list " "of str.", rule=self
                        )
                    concrete = concretize(item_, wildcards, _is_callable)
                    newitems.append(concrete)
                    if mapping is not None:
                        mapping[concrete] = item_

                if name:
                    newitems.set_name(
                        name, start, end=len(newitems) if is_iterable else None
                    )
                    start = len(newitems)