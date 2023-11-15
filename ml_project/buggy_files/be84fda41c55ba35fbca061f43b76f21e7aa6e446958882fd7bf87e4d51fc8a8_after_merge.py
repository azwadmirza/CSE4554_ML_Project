    def expand_params(self, wildcards, input, output, resources, omit_callable=False):
        def concretize_param(p, wildcards, is_from_callable):
            if not is_from_callable:
                if isinstance(p, str):
                    return apply_wildcards(p, wildcards)
                if isinstance(p, list):
                    return [
                        (apply_wildcards(v, wildcards) if isinstance(v, str) else v)
                        for v in p
                    ]
            return p

        params = Params()
        try:
            # When applying wildcards to params, the return type need not be
            # a string, so the check is disabled.
            self._apply_wildcards(
                params,
                self.params,
                wildcards,
                concretize=concretize_param,
                check_return_type=False,
                omit_callable=omit_callable,
                allow_unpack=False,
                no_flattening=True,
                apply_default_remote=False,
                aux_params={
                    "input": input._plainstrings(),
                    "resources": resources,
                    "output": output._plainstrings(),
                    "threads": resources._cores,
                },
                incomplete_checkpoint_func=lambda e: "<incomplete checkpoint>",
            )
        except WildcardError as e:
            raise WildcardError(
                "Wildcards in params cannot be "
                "determined from output files. Note that you have "
                "to use a function to deactivate automatic wildcard expansion "
                "in params strings, e.g., `lambda wildcards: '{test}'`. Also "
                "see https://snakemake.readthedocs.io/en/stable/snakefiles/"
                "rules.html#non-file-parameters-for-rules:",
                str(e),
                rule=self,
            )
        return params