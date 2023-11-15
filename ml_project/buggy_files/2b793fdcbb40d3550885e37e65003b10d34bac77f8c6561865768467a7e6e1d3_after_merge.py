    def convert_search_space(spec: Dict,
                             join: bool = False) -> Dict[str, Tuple]:
        spec = copy.deepcopy(spec)
        resolved_vars, domain_vars, grid_vars = parse_spec_vars(spec)

        if not domain_vars and not grid_vars:
            return {}

        if grid_vars:
            raise ValueError(
                "Grid search parameters cannot be automatically converted "
                "to a ZOOpt search space.")

        def resolve_value(domain: Domain) -> Tuple:
            quantize = None

            sampler = domain.get_sampler()
            if isinstance(sampler, Quantized):
                quantize = sampler.q
                sampler = sampler.sampler

            if isinstance(domain, Float):
                precision = quantize or 1e-12
                if isinstance(sampler, Uniform):
                    return (ValueType.CONTINUOUS, [domain.lower, domain.upper],
                            precision)

            elif isinstance(domain, Integer):
                if isinstance(sampler, Uniform):
                    return (ValueType.DISCRETE, [domain.lower, domain.upper],
                            True)

            elif isinstance(domain, Categorical):
                # Categorical variables would use ValueType.DISCRETE with
                # has_partial_order=False, however, currently we do not
                # keep track of category values and cannot automatically
                # translate back and forth between them.
                if isinstance(sampler, Uniform):
                    return (ValueType.GRID, domain.categories)

            raise ValueError("ZOOpt does not support parameters of type "
                             "`{}` with samplers of type `{}`".format(
                                 type(domain).__name__,
                                 type(domain.sampler).__name__))

        conv_spec = {
            "/".join(path): resolve_value(domain)
            for path, domain in domain_vars
        }

        if join:
            spec.update(conv_spec)
            conv_spec = spec

        return conv_spec